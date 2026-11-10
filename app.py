
import os
import re
import hmac
import secrets
import sqlite3

from datetime import timedelta
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    session,
    g,
    flash,
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# --------------------------------------------------
# FLASK-LIMITER: GLOBAL INSTANCE
# Keeps the limiter alive across application instances.
# --------------------------------------------------

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://",
)


# --------------------------------------------------
# HTML TEMPLATE
# --------------------------------------------------

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{{ title }} | Secure Authentication Lab</title>

    <link rel="stylesheet"
          href="{{ url_for('static', filename='style.css') }}">

    <style>
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #080d25, #17133e, #101c38);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .card {
            width: 90%;
            max-width: 430px;
            padding: 35px;
            box-sizing: border-box;
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 20px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.35);
            backdrop-filter: blur(15px);
        }

        h1 {
            text-align: center;
            color: #a5b4fc;
            margin-bottom: 8px;
        }

        .subtitle {
            text-align: center;
            color: #b8c2dc;
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-top: 16px;
            margin-bottom: 7px;
            color: #dce5ff;
        }

        input {
            width: 100%;
            padding: 13px;
            box-sizing: border-box;
            border: 1px solid #49557e;
            border-radius: 9px;
            background: #101a35;
            color: white;
            outline: none;
        }

        input:focus {
            border-color: #818cf8;
            box-shadow: 0 0 8px #6366f1;
        }

        button, .button {
            display: block;
            width: 100%;
            margin-top: 22px;
            padding: 13px;
            border: none;
            border-radius: 9px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            color: white;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            box-sizing: border-box;
        }

        button:hover, .button:hover {
            opacity: 0.9;
        }

        .message {
            padding: 12px;
            margin-bottom: 15px;
            background: rgba(99,102,241,0.2);
            border: 1px solid #6366f1;
            border-radius: 8px;
            color: #e0e7ff;
        }

        .links {
            text-align: center;
            margin-top: 20px;
            color: #cbd5e1;
        }

        a {
            color: #a5b4fc;
            text-decoration: none;
        }

        .status {
            text-align: center;
            color: #86efac;
            font-size: 13px;
            margin-bottom: 20px;
        }

        .footer {
            margin-top: 25px;
            text-align: center;
            color: #8995b5;
            font-size: 12px;
        }
    </style>
</head>

<body>
    <main class="card">

        <h1>SECURE AUTH</h1>

        <p class="subtitle">
            Secure Authentication Lab
        </p>

        <div class="status">
            ● SYSTEM ONLINE
        </div>

        {% with messages = get_flashed_messages() %}
            {% for message in messages %}
                <div class="message">{{ message }}</div>
            {% endfor %}
        {% endwith %}

        {% if page == "home" %}

            <h2>Welcome</h2>
            <p>Explore our secure authentication system.</p>

            <a class="button" href="{{ url_for('login') }}">
                Login
            </a>

            <a class="button" href="{{ url_for('register') }}">
                Create Account
            </a>

        {% elif page == "register" %}

            <h2>Create Account</h2>

            <form method="POST" action="{{ url_for('register') }}">

                <input type="hidden"
                       name="csrf_token"
                       value="{{ csrf_token }}">

                <label>Username</label>
                <input type="text"
                       name="username"
                       minlength="3"
                       maxlength="30"
                       required>

                <label>Password</label>
                <input type="password"
                       name="password"
                       minlength="12"
                       maxlength="128"
                       required>

                <button type="submit">Register Securely</button>

            </form>

            <div class="links">
                Already registered?
                <a href="{{ url_for('login') }}">Login</a>
            </div>

        {% elif page == "login" %}

            <h2>Welcome Back</h2>

            <form method="POST" action="{{ url_for('login') }}">

                <input type="hidden"
                       name="csrf_token"
                       value="{{ csrf_token }}">

                <label>Username</label>
                <input type="text"
                       name="username"
                       maxlength="30"
                       required>

                <label>Password</label>
                <input type="password"
                       name="password"
                       maxlength="128"
                       required>

                <button type="submit">Login Securely</button>

            </form>

            <div class="links">
                New user?
                <a href="{{ url_for('register') }}">Register</a>
            </div>

        {% elif page == "dashboard" %}

            <h2>Dashboard</h2>

            <p>Welcome, {{ username }}!</p>

            <p>Your authentication was successful.</p>

            <p class="status">● AUTHENTICATED</p>

            <form method="POST" action="{{ url_for('logout') }}">

                <input type="hidden"
                       name="csrf_token"
                       value="{{ csrf_token }}">

                <button type="submit">Sign Out Securely</button>

            </form>

        {% endif %}

        <div class="footer">
            Secure Authentication Lab | Cyber Security Project
        </div>

    </main>
</body>
</html>
"""


# --------------------------------------------------
# APPLICATION FACTORY
# --------------------------------------------------

def create_app(test_config=None):

    app = Flask(__name__)

    project_folder = Path(__file__).resolve().parent
    instance_folder = project_folder / "instance"

    instance_folder.mkdir(exist_ok=True)

    app.config.update(
        SECRET_KEY=os.environ.get(
            "SECRET_KEY",
            "local-development-key-change-before-deployment"
        ),

        DATABASE=str(instance_folder / "auth.db"),

        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
        SESSION_COOKIE_SAMESITE="Lax",

        PERMANENT_SESSION_LIFETIME=timedelta(minutes=15),
        SESSION_REFRESH_EACH_REQUEST=False,

        MAX_CONTENT_LENGTH=16 * 1024,

        RATELIMIT_ENABLED=True,
    )

    if test_config:
        app.config.update(test_config)

    # Initialize the globally retained limiter.
    limiter.init_app(app)

    app.extensions["limiter_instance"] = limiter

    # --------------------------------------------------
    # DATABASE
    # --------------------------------------------------

    def initialize_database():

        database_path = app.config["DATABASE"]

        if database_path != ":memory:":
            Path(database_path).parent.mkdir(
                parents=True,
                exist_ok=True
            )

        connection = sqlite3.connect(database_path)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    initialize_database()

    def get_db():

        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row

        return g.db

    @app.teardown_appcontext
    def close_db(error=None):

        database = g.pop("db", None)

        if database is not None:
            database.close()

    # --------------------------------------------------
    # PASSWORD VALIDATION
    # --------------------------------------------------

    def valid_username(username):

        return bool(
            re.fullmatch(r"[A-Za-z0-9_]{3,30}", username)
        )

    def valid_password(password):

        return (
            len(password) >= 12
            and len(password) <= 128
            and re.search(r"[A-Z]", password)
            and re.search(r"[a-z]", password)
            and re.search(r"\d", password)
        )

    # --------------------------------------------------
    # CSRF PROTECTION
    # --------------------------------------------------

    def generate_csrf_token():

        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)

        return session["csrf_token"]

    def validate_csrf_token():

        submitted_token = request.form.get("csrf_token", "")
        stored_token = session.get("csrf_token", "")

        return (
            bool(submitted_token)
            and bool(stored_token)
            and hmac.compare_digest(
                submitted_token,
                stored_token
            )
        )

    # --------------------------------------------------
    # SESSION PROTECTION
    # --------------------------------------------------

    def login_required(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                flash("Please log in to access the dashboard.")
                return redirect(url_for("login"))

            return function(*args, **kwargs)

        return wrapper

    # --------------------------------------------------
    # HOME
    # --------------------------------------------------

    @app.route("/")
    def home():

        return render_template_string(
            PAGE,
            title="Home",
            page="home",
            csrf_token=generate_csrf_token()
        )

    # --------------------------------------------------
    # REGISTER
    # --------------------------------------------------

    @app.route("/register", methods=["GET", "POST"])
    def register():

        if request.method == "POST":

            if not validate_csrf_token():
                flash("Invalid form request. Please try again.")
                return redirect(url_for("register"))

            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not valid_username(username):
                flash("Username must be 3-30 characters using letters, numbers or underscores.")

            elif not valid_password(password):
                flash("Password must be 12-128 characters and include uppercase, lowercase and a number.")

            else:

                password_hash = generate_password_hash(
                    password,
                    method="scrypt"
                )

                database = get_db()

                try:

                    database.execute(
                        """
                        INSERT INTO users (username, password_hash)
                        VALUES (?, ?)
                        """,
                        (username, password_hash)
                    )

                    database.commit()

                    session.clear()

                    flash("Registration successful. Please log in.")

                    return redirect(url_for("login"))

                except sqlite3.IntegrityError:

                    database.rollback()

                    flash("Registration could not be completed.")

        return render_template_string(
            PAGE,
            title="Register",
            page="register",
            csrf_token=generate_csrf_token()
        )

    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("5 per minute", methods=["POST"])
    def login():

        if request.method == "POST":

            if not validate_csrf_token():
                flash("Invalid form request. Please try again.")
                return redirect(url_for("login"))

            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            database = get_db()

            user = database.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            if user:

                password_valid = check_password_hash(
                    user["password_hash"],
                    password
                )

            else:

                # Dummy hash check helps reduce timing differences.
                check_password_hash(
                    generate_password_hash(
                        "dummy-password-value",
                        method="scrypt"
                    ),
                    password
                )

                password_valid = False

            if user and password_valid:

                session.clear()

                session.permanent = True

                session["user_id"] = user["id"]
                session["username"] = user["username"]

                generate_csrf_token()

                return redirect(url_for("dashboard"))

            flash("Invalid username or password.")

        return render_template_string(
            PAGE,
            title="Login",
            page="login",
            csrf_token=generate_csrf_token()
        )

    # --------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------

    @app.route("/dashboard")
    @login_required
    def dashboard():

        return render_template_string(
            PAGE,
            title="Dashboard",
            page="dashboard",
            username=session.get("username"),
            csrf_token=generate_csrf_token()
        )

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------

    @app.route("/logout", methods=["POST"])
    def logout():

        if not validate_csrf_token():
            flash("Invalid form request.")
            return redirect(url_for("home"))

        session.clear()

        flash("You have successfully logged out.")

        return redirect(url_for("home"))

    return app


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

app = create_app()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
