from flask import Flask, request, jsonify
import psycopg2
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# Database connection
# -----------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set. Please configure Render environment variable.")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# -----------------------------
# Create table automatically
# -----------------------------
def create_users_table():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

# Run table creation on startup
create_users_table()

# -----------------------------
# Register
# -----------------------------
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User registered successfully"})

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Username already exists"}), 409

    except Exception as e:
        return jsonify({"error": f"REGISTER ERROR: {str(e)}"}), 500


# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, password FROM users WHERE username = %s",
            (username,)
        )

        user = cur.fetchone()

        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        user_id, stored_password = user

        if not check_password_hash(stored_password, password):
            return jsonify({"error": "Invalid username or password"}), 401

        # Update last login time
        cur.execute(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.now(), user_id)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Login successful"})

    except Exception as e:
        return jsonify({"error": f"LOGIN ERROR: {str(e)}"}), 500


# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return "Render PostgreSQL is connected successfully!"

# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
