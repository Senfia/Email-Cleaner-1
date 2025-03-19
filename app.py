
from flask import Flask, render_template, request, jsonify
import os
import time
import threading
import re
import dns.resolver
import csv
from typing import List, Dict, Tuple

app = Flask(__name__)

# Global variable to track progress
progress = {
    "total": 0,
    "processed": 0,
    "valid": 0,
    "invalid": 0,
    "status": "idle",
    "current_email": ""
}

def reset_progress():
    """Reset the progress tracker."""
    global progress
    progress = {
        "total": 0,
        "processed": 0,
        "valid": 0,
        "invalid": 0,
        "status": "idle",
        "current_email": ""
    }

def is_valid_email_format(email: str) -> bool:
    """Check if the email address format is valid."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def check_mx_record(domain: str) -> bool:
    """Check if the domain has valid MX records."""
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return len(answers) > 0
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
        return False

def validate_email(email: str) -> bool:
    """Validate email format and MX record."""
    if not is_valid_email_format(email):
        return False
    
    # Extract domain from email
    domain = email.split('@')[1]
    return check_mx_record(domain)

def process_csv_file(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """Process the CSV file in a separate thread with progress updates."""
    global progress
    
    progress["status"] = "processing"
    valid_entries = []
    invalid_entries = []
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            progress["total"] = len(rows)
            
            for row in rows:
                first_name = row.get('First Name', '')
                last_name = row.get('Last Name', '')
                email = row.get('Email', '')
                
                entry = {
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Email': email
                }
                
                progress["current_email"] = email
                
                if email and validate_email(email):
                    valid_entries.append(entry)
                    progress["valid"] += 1
                else:
                    invalid_entries.append(entry)
                    progress["invalid"] += 1
                
                progress["processed"] += 1
                # Small delay to make progress visible in the UI
                time.sleep(0.1)
        
        # Save the results
        output_dir = os.path.join(app.root_path, 'static', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        valid_path = os.path.join(output_dir, 'valid_emails.csv')
        invalid_path = os.path.join(output_dir, 'invalid_emails.csv')
        
        if valid_entries:
            with open(valid_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = valid_entries[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(valid_entries)
        
        if invalid_entries:
            with open(invalid_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = invalid_entries[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(invalid_entries)
                
        progress["status"] = "completed"
        
    except Exception as e:
        progress["status"] = f"error: {str(e)}"
    
    return valid_entries, invalid_entries

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start processing."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and file.filename.endswith('.csv'):
        reset_progress()
        
        # Save the file
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, 'input.csv')
        file.save(file_path)
        
        # Start processing in a separate thread
        thread = threading.Thread(target=process_csv_file, args=(file_path,))
        thread.daemon = True
        thread.start()
        
        return jsonify({"message": "File uploaded and processing started"})
    else:
        return jsonify({"error": "Only CSV files are allowed"}), 400

@app.route('/progress')
def get_progress():
    """Return the current progress as JSON."""
    return jsonify(progress)

@app.route('/download/<file_type>')
def download_file(file_type):
    """Provide download links for the processed files."""
    if file_type not in ['valid', 'invalid']:
        return jsonify({"error": "Invalid file type"}), 400
    
    filename = f"{file_type}_emails.csv"
    file_path = os.path.join(app.root_path, 'static', 'output', filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    return app.send_static_file(f"output/{filename}")

if __name__ == '__main__':
    app.run(debug=True)