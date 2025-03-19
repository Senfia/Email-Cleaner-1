# Email Cleaner

Email Cleaner is a web application built with Flask that allows users to upload a CSV file containing email addresses. The application validates the email addresses and provides a downloadable list of valid and invalid emails.

## Features

- Upload CSV files containing email addresses.
- Validate email addresses based on format and MX records.
- Track the progress of email validation.
- Download lists of valid and invalid email addresses.

## Requirements

- Python 3.7+
- Flask
- dnspython

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Senfia/email-cleaner.git
    cd email-cleaner
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # or
    source venv/bin/activate  # On macOS/Linux
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Flask application:

    ```bash
    python app.py
    ```

2. Open your web browser and go to `http://127.0.0.1:5000`.

3. Upload a CSV file containing email addresses.

4. Monitor the progress of email validation.

5. Download the lists of valid and invalid email addresses.

## Project Structure

```
email-cleaner/
├── static/
├── output/
├── uploads/
├── templates/
│   └── index.html
├── app.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.