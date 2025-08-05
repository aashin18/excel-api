# Address Validator API

Flask API for validating addresses against location data.

## Setup and Deployment Instructions

### Local Development

1. Create a virtual environment and activate it:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Unix/Mac
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application locally:
   ```
   flask run
   ```

### Heroku Deployment

1. Initialize a Git repository (if not already done):
   ```
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Install Heroku CLI (if not already installed) from https://devcenter.heroku.com/articles/heroku-cli

3. Log in to Heroku:
   ```
   heroku login
   ```

4. Create a Heroku app:
   ```
   heroku create your-app-name
   ```

5. Push to Heroku:
   ```
   git push heroku main
   ```

6. Check if the app is running:
   ```
   heroku open
   ```

## API Endpoints

### Health Check
- **URL**: `/health`
- **Method**: GET
- **Response**: `{"status": "healthy"}`

### Upload Location Data
- **URL**: `/upload-locations`
- **Method**: POST
- **Form Data**: `file` (CSV file with 'location' and 'Code' columns)
- **Response**: Information about uploaded data

### Validate Address
- **URL**: `/validate`
- **Method**: POST
- **JSON Payload**:
  ```json
  {
    "address": "123 Main St, New York",
    "facilityCode": "NYC"
  }
  ```
- **Response**: Validation result with matches

### Process Excel File
- **URL**: `/process`
- **Method**: POST
- **Form Data**: `file` (Excel file with addresses and facility codes)
- **Response**: Detailed processing results with statistics

## Example Usage

Using curl to test the API:

```bash
# Health check
curl https://your-app-name.herokuapp.com/health

# Upload location data
curl -X POST -F "file=@lists.csv" https://your-app-name.herokuapp.com/upload-locations

# Validate a single address
curl -X POST -H "Content-Type: application/json" -d '{"address":"123 Main St, New York", "facilityCode":"NYC"}' https://your-app-name.herokuapp.com/validate

# Process Excel file
curl -X POST -F "file=@input_file.xlsx" https://your-app-name.herokuapp.com/process
```
