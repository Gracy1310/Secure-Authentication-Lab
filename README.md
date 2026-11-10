# Secure Authentication Lab

## Project Overview
Secure Authentication Lab is a Python Flask-based web application demonstrating essential authentication security practices.

The application allows users to register, log in, access a protected dashboard, and securely log out.

## Technologies Used
- Python
- Flask
- SQLite
- Flask-Limiter
- Werkzeug Password Hashing
- HTML and CSS
- Pytest

## Features
1. User registration and login.
2. Password hashing using Scrypt.
3. Password strength validation.
4. CSRF token validation.
5. Login rate limiting.
6. Protected dashboard.
7. Secure session cookie settings.
8. Logout functionality.
9. Automated security tests.

## Project Structure
```text
Secure_Authentication_Lab/
├── app.py
├── test_app.py
├── requirements.txt
├── .gitignore
├── static/
│   └── style.css
└── instance/
    └── auth.db
```

The `instance/` directory contains the local SQLite database and is excluded from Git.

## Installation

### 1. Clone the repository
```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Secure_Authentication_Lab
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate the environment

Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set a secret key

Windows PowerShell:
```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Run the application
```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Run Automated Tests
```bash
python -m pytest -v
```

## Test Results
The current automated test suite contains five tests:

- Home page test
- User registration test
- Password hashing test
- Invalid login rejection test
- Protected dashboard test

Latest local test result: **5 passed**.

## Security Considerations
This is an educational security lab, not a production-ready authentication service. Review `SECURITY_NOTE.md` for implementation details and limitations.

## Author
Cyber Security Student

## Project Purpose
To understand and demonstrate practical authentication security concepts through a hands-on Python application.