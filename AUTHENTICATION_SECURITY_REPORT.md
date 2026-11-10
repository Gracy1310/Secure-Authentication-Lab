# AUTHENTICATION SECURITY REPORT

## 1. Project Overview

The Secure Authentication Lab is a Python-based web application developed using Flask. The main objective of this project is to implement and demonstrate essential security practices used in user authentication systems.

The application provides user registration, secure password storage, login validation, session management, CSRF protection, and login rate limiting.

## 2. Technologies Used

- **Programming Language:** Python
- **Web Framework:** Flask
- **Database:** SQLite
- **Password Hashing:** Scrypt
- **Security Library:** Flask-Limiter
- **Testing Framework:** Pytest
- **Frontend:** HTML and CSS

## 3. Security Features Implemented

### 3.1 Secure Password Hashing

- Passwords are not stored in plain text.
- Werkzeug's password hashing functionality is used with the Scrypt algorithm.
- Password hashes are stored in the SQLite database.
- This helps protect user passwords if database contents are exposed.

### 3.2 Password Validation

The application validates passwords before registration.

Implemented requirements include:

- Minimum length of 12 characters.
- Maximum length of 128 characters.
- At least one uppercase letter.
- At least one lowercase letter.
- At least one numeric digit.

### 3.3 Username Validation

- Usernames must contain 3 to 30 characters.
- Only letters, numbers, and underscores are accepted.
- Invalid usernames are rejected during registration.

### 3.4 Login Security

- Registered users can log in using their username and password.
- Incorrect login credentials are rejected.
- A generic error message is used to avoid revealing whether a username exists.
- Passwords are verified against their stored hashes.

### 3.5 Login Rate Limiting

Flask-Limiter is used to restrict repeated login attempts.

- Maximum of 5 login attempts per minute.
- Excessive attempts receive a `429 Too Many Requests` response.
- This helps reduce automated password-guessing attempts.

**Note:** The current rate limiter uses in-memory storage and is intended for local testing.

### 3.6 CSRF Protection

- CSRF tokens are generated using Python's secure random token generation.
- Tokens are stored in the Flask session.
- Protected form submissions validate the token.
- Constant-time comparison is used for token verification.

### 3.7 Session and Cookie Security

The application includes the following cookie security settings:

- HttpOnly enabled.
- SameSite set to Lax.
- Secure cookie option available for HTTPS deployment.
- Flask session cookie lifetime configured to 15 minutes.

**Note:** Flask's default session implementation uses signed client-side cookies. The configured cookie lifetime is not a server-enforced idle-session timeout.

### 3.8 Protected Dashboard and Logout

- The dashboard is accessible only to authenticated users.
- Unauthenticated users are redirected to the login page.
- Logout is performed using a POST request with CSRF validation.
- After logout, users cannot access the protected dashboard without logging in again.

### 3.9 Database Security

- SQLite is used to store registered user information.
- Parameterized SQL queries are used for database operations.
- Password hashes are stored instead of plain-text passwords.
- The local database file is excluded from Git using `.gitignore`.

## 4. Application Testing

The application was tested using Pytest.

The following automated test cases were executed:

| Test Case | Description | Result |
|---|---|---|
| Test 1 | Home page loads successfully | PASS |
| Test 2 | User registration works | PASS |
| Test 3 | Password is stored as a Scrypt hash | PASS |
| Test 4 | Invalid login is rejected | PASS |
| Test 5 | Dashboard requires authentication | PASS |

### Test Execution

Command used:

```powershell
python -m pytest -v
```

**Final Test Result:**

```text
5 passed in 1.93s
```

All five automated test cases passed successfully.

## 5. Security Limitations

This project is developed as an educational security lab and is not intended to be deployed directly as a production authentication service.

Possible future improvements include:

- Implementing server-side session management.
- Using persistent rate-limit storage such as Redis.
- Adding password reset functionality.
- Implementing multi-factor authentication (MFA).
- Adding account lockout and security monitoring.
- Deploying behind HTTPS with production-grade configuration.

## 6. Conclusion

The Secure Authentication Lab demonstrates the implementation of important authentication security practices using Python and Flask.

The project successfully implements secure password hashing, input validation, login rate limiting, CSRF protection, session cookie security, protected routes, and automated testing.

The successful execution of all five test cases confirms that the implemented core authentication features work as expected in the local testing environment.

This project provided practical experience in developing and testing a basic secure authentication application.