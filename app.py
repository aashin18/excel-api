from flask import Flask, request, jsonify
import pandas as pd
import io
import re
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Store location data in memory (in a production app, use a database)
locations_df = pd.DataFrame()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/upload-locations', methods=['POST'])
def upload_locations():
    """Upload location data CSV file"""
    global locations_df
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if file and file.filename.endswith('.csv'):
        try:
            # Read CSV file
            content = file.read()
            locations_df = pd.read_csv(io.BytesIO(content))
            
            # Validate structure
            required_columns = ['location', 'Code']
            if not all(col in locations_df.columns for col in required_columns):
                return jsonify({"error": f"CSV must contain columns: {required_columns}"}), 400
                
            # Save a local copy for persistence
            locations_df.to_csv('locations.csv', index=False)
            
            return jsonify({
                "message": "Location data uploaded successfully",
                "rows": len(locations_df),
                "columns": list(locations_df.columns)
            }), 200
        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    else:
        return jsonify({"error": "Only CSV files are allowed"}), 400

@app.route('/validate', methods=['POST'])
def validate_address():
    """Validate a single address against the location data"""
    global locations_df
    
    # Load locations from file if not already loaded
    if locations_df.empty and os.path.exists('locations.csv'):
        locations_df = pd.read_csv('locations.csv')
    
    if locations_df.empty:
        return jsonify({"error": "No location data available. Please upload location data first."}), 400
    
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    address = data.get('address')
    dst_fac_code = data.get('facilityCode')
    
    if not address:
        return jsonify({"error": "Address is required"}), 400
    
    if not dst_fac_code:
        return jsonify({"error": "Facility code is required"}), 400
    
    # Perform address validation
    validity, matches = check_address_match(address, dst_fac_code, locations_df)
    
    # Format matches for JSON response
    formatted_matches = [{"location": loc, "code": code} for loc, code in matches]
    
    return jsonify({
        "address": address,
        "facilityCode": dst_fac_code,
        "validity": validity,
        "matches": formatted_matches
    }), 200

@app.route('/process', methods=['POST'])
def process_file():
    """Process an Excel file with addresses"""
    global locations_df
    
    # Load locations from file if not already loaded
    if locations_df.empty and os.path.exists('locations.csv'):
        locations_df = pd.read_csv('locations.csv')
    
    if locations_df.empty:
        return jsonify({"error": "No location data available. Please upload location data first."}), 400
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            temp_path = os.path.join('/tmp', filename)
            file.save(temp_path)
            
            # Process the file
            df = pd.read_excel(temp_path)
            
            # Process using the same logic as in the original script
            # Clear first 2 rows
            df.iloc[0] = None
            df.iloc[1] = None
            
            # Find columns with specific values in 3rd row
            target_columns = ["HWB", "Dst Fac", "Prod Cd", "# Pcs\\Tot Pcs", "Wt", 
                             "Cnee Addr Ln 1", "Cnee Addr Ln 2", "Cnee Addr Ln 3"]
            
            columns_to_keep = []
            for col_index, value in enumerate(df.iloc[2]):
                value_str = str(value).strip()
                for target in target_columns:
                    if value_str.lower() == target.lower():
                        columns_to_keep.append(col_index)
                        break
            
            if not columns_to_keep:
                return jsonify({"error": "No target columns found in 3rd row!"}), 400
            
            # Keep only target columns
            df_filtered = df.iloc[:, columns_to_keep]
            
            # Set column names from 3rd row
            new_headers = []
            for col_idx in range(len(df_filtered.columns)):
                header = str(df_filtered.iloc[2, col_idx]).strip()
                new_headers.append(header)
            df_filtered.columns = new_headers
            
            # Merge address columns
            addr_columns = ["Cnee Addr Ln 1", "Cnee Addr Ln 2", "Cnee Addr Ln 3"]
            existing_addr_cols = [col for col in addr_columns if col in df_filtered.columns]
            
            if existing_addr_cols:
                # Create merged address
                df_filtered['Address'] = df_filtered[existing_addr_cols].apply(
                    lambda row: ' '.join([str(val) for val in row if pd.notna(val) and str(val).strip() != '']), 
                    axis=1
                )
                
                # Drop original address columns
                df_filtered = df_filtered.drop(columns=existing_addr_cols)
            
            # Remove the first 3 rows (headers and empty rows)
            df_final = df_filtered.iloc[3:].reset_index(drop=True)
            
            # Add validity check
            results = []
            if 'Address' in df_final.columns and 'Dst Fac' in df_final.columns:
                for idx, row in df_final.iterrows():
                    address = row['Address']
                    dst_fac = row['Dst Fac']
                    
                    validity, matches = check_address_match(address, dst_fac, locations_df)
                    df_final.at[idx, 'Validity'] = validity
                    
                    row_dict = row.to_dict()
                    row_dict['Validity'] = validity
                    row_dict['MatchDetails'] = [{"location": loc, "code": code} for loc, code in matches]
                    results.append(row_dict)
            
            # Calculate statistics
            validity_stats = {}
            if 'Validity' in df_final.columns:
                validity_counts = df_final['Validity'].value_counts().to_dict()
                validity_stats = {
                    'Match': validity_counts.get('Match', 0),
                    'Mismatch': validity_counts.get('Mismatch', 0),
                    'No Match': validity_counts.get('No Match', 0),
                    'Multi Match': validity_counts.get('Multi Match', 0)
                }
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return jsonify({
                "message": "File processed successfully",
                "totalRows": len(df_final),
                "statistics": validity_stats,
                "results": results
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    else:
        return jsonify({"error": "Only Excel files (.xlsx, .xls) are allowed"}), 400

def check_address_match(address, dst_fac_code, location_data):
    """Check if address matches any location in the data"""
    if pd.isna(address) or str(address).strip() == '':
        return 'No Match', []
    
    address_to_check = str(address).strip().lower()
    dst_fac_code = str(dst_fac_code).strip().upper()
    
    # Normalize address by replacing various special characters with spaces
    normalized_address = address_to_check
    # Replace common separators with spaces
    for char in ['-', ',', '.', '/', '\\', '&', '+', '(', ')', '[', ']', '{', '}', '|', ';', ':', '"', "'", '`']:
        normalized_address = normalized_address.replace(char, ' ')
    # Remove extra spaces
    normalized_address = ' '.join(normalized_address.split())
    
    # Track all matches found
    matched_codes = set()
    matched_locations = []
    
    # Check each location in the data
    for _, row in location_data.iterrows():
        location = str(row['location']).strip().lower()
        code = str(row['Code']).strip().upper()
        
        # Skip empty locations
        if not location:
            continue
            
        # Normalize location with same character replacements
        normalized_location = location
        for char in ['-', ',', '.', '/', '\\', '&', '+', '(', ')', '[', ']', '{', '}', '|', ';', ':', '"', "'", '`']:
            normalized_location = normalized_location.replace(char, ' ')
        normalized_location = ' '.join(normalized_location.split())
        
        # Check for exact match using regex word boundaries
        match_found = False
        
        # Create regex pattern for exact location matching
        escaped_location = re.escape(normalized_location)
        pattern = r'\b' + escaped_location + r'\b'
        
        # Check if the exact location exists in the address
        if re.search(pattern, normalized_address):
            match_found = True
        
        if match_found:
            matched_codes.add(code)
            matched_locations.append((normalized_location, code))
    
    # Determine validity based on matches found
    if len(matched_codes) > 1:
        return 'Multi Match', matched_locations
    elif len(matched_codes) == 1:
        matched_code = list(matched_codes)[0]
        if matched_code == dst_fac_code:
            return 'Match', matched_locations
        else:
            return 'Mismatch', matched_locations
    else:
        return 'No Match', []

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
