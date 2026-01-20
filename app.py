from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import psycopg2.extras
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret_key_123")

# ==========================
# DATABASE CONNECTION
# ==========================
def get_db():
    return psycopg2.connect(
        os.environ.get("DATABASE_URL"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

# ==========================
# ROUTES
# ==========================

@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:
            db = get_db()
            cur = db.cursor()

            cur.execute(
                "INSERT INTO users (username, password, created_at) VALUES (%s, %s, %s)",
                (username, password, datetime.now())
            )

            db.commit()
            cur.close()
            db.close()

            return redirect(url_for('login'))

        except Exception as e:
            return f"Error: {e}"

    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()

        cur.close()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            return redirect(url_for('dashboard'))

        return "Invalid username or password"

    return render_template('login.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', user=session['user'])

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ==========================
# RUN (Local only)
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
