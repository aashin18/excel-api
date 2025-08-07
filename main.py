from flask import Flask, request, jsonify
import pandas as pd
import base64
import os

app = Flask(__name__)

def process_excel_file():
    # Load the input Excel file
    df = pd.read_excel("input_file.xlsx")

    # Normalize address columns
    df["Cnee Addr Ln 1"] = df["Cnee Addr Ln 1"].astype(str).str.upper().str.replace(r"[^A-Z0-9\s]", "", regex=True)
    df["Cnee Addr Ln 2"] = df["Cnee Addr Ln 2"].astype(str).str.upper().str.replace(r"[^A-Z0-9\s]", "", regex=True)
    df["Cnee Addr Ln 3"] = df["Cnee Addr Ln 3"].astype(str).str.upper().str.replace(r"[^A-Z0-9\s]", "", regex=True)

    # Load the CSV file
    with open("lists.csv", "r", encoding="utf-8") as f:
        lines = f.readlines()

    area_dict = {}
    for line in lines:
        key, values = line.strip().split(":", 1)
        area_dict[key] = [v.strip().upper() for v in values.split(",")]

    def check_address(row):
        matches = set()
        for key, values in area_dict.items():
            for val in values:
                if (val in row["Cnee Addr Ln 1"]) or (val in row["Cnee Addr Ln 2"]) or (val in row["Cnee Addr Ln 3"]):
                    matches.add(key)
        if len(matches) == 1:
            return list(matches)[0]
        elif len(matches) > 1:
            return "Multi Match"
        else:
            return "No Match"

    df["Address Match"] = df.apply(check_address, axis=1)

    # Save the processed Excel file
    df.to_excel("output_file.xlsx", index=False)

@app.route('/')
def index():
    return 'Flask app is running!'

@app.route('/process', methods=['POST'])
def process_base64():
    try:
        data = request.get_json()

        # Get base64 strings from JSON
        input_file_b64 = data.get('input_file_base64')
        list_file_b64 = data.get('list_file_base64')

        if not input_file_b64 or not list_file_b64:
            return jsonify({"status": "error", "message": "Missing required base64 file(s)"}), 400

        # Decode and write input_file.xlsx
        with open("input_file.xlsx", "wb") as f:
            f.write(base64.b64decode(input_file_b64))

        # Decode and write lists.csv
        with open("lists.csv", "wb") as f:
            f.write(base64.b64decode(list_file_b64))

        # Call your existing logic
        process_excel_file()

        # Read and encode the output file
        with open("output_file.xlsx", "rb") as f:
            output_b64 = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            "status": "success",
            "output_file_base64": output_b64
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
