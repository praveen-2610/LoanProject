import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
import pickle
import pandas as pd

app = Flask(__name__)

@app.route("/test")
def test():
    return "Flask is working perfectly!"

# ---------------- DATABASE ----------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="username",
            password="password",
            database="databasename",
            connection_timeout=5
        )
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("model/loan_model.pkl", "rb"))
scaler = pickle.load(open("model/scaler.pkl", "rb"))

# ---------------- PAGES ----------------
@app.route("/")
def home():
    return render_template("Signup.html")

@app.route("/signin")
def signin():
    return render_template("Signin.html")

@app.route("/index")
def index():
    return render_template("Index1.html")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    try:
        if request.method == "GET":
            return redirect(url_for("home"))

        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmPassword")

        # 🔴 VALIDATION FIRST
        if not username or not password or not confirm:
            return render_template("Signup.html", message="Please fill all fields!")

        if password.strip() != confirm.strip():
            return render_template("Signup.html", message="Passwords do not match!")

        # 🟢 CONNECT DB AFTER VALIDATION
        conn = get_db_connection()
        if conn is None:
            return "❌ DB CONNECTION FAILED"

        cursor = conn.cursor()

        # 🔴 CHECK EXISTING USER
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()
            return render_template("Signup.html", message="Username already exists!")

        # 🟢 INSERT NEW USER
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        conn.commit()

        cursor.close()
        conn.close()

        # ✅ SUCCESS → GO TO SIGNIN
        return redirect(url_for("signin"))

    except Exception as e:
        return f"<h3>Error: {str(e)}</h3>"
# ---------------- SIGNIN ----------------
@app.route("/login", methods=["POST"])
def login():
    try:
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        if conn is None:
            return render_template("Signin.html", message="Database connection failed")

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return redirect(url_for("index"))
        else:
            # ❌ WRONG LOGIN → stay on signin page
            return render_template("Signin.html", message="Invalid Username or Password")

    except Exception as e:
        return render_template("Signin.html", message=str(e))

# ---------------- PREDICTION ----------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        f1 = int(request.form.get("dependents", 0))
        f2 = int(request.form.get("education", 0))
        f3 = int(request.form.get("self_employed", 0))
        f4 = int(request.form.get("income_annum", 0))
        f5 = int(request.form.get("loan_amount", 0))
        f6 = int(request.form.get("loan_term", 0))
        f7 = int(request.form.get("cibil_score", 0))
        f8 = int(request.form.get("assets", 0))

        features = [f1, f2, f3, f4, f5, f6, f7, f8]

        columns = ["no_of_dependents","education","self_employed","income_annum",
                   "loan_amount","loan_term","cibil_score","Assets"]

        scaled_features = scaler.transform([features])
        try:
            prob = model.predict_proba(scaled_features)[0][1]
        except Exception as e:
            return f"MODEL ERROR: {str(e)}"

        if prob >= 0.65:
            result = "Approved"
            reason = "High CIBIL score, sufficient income and good assets."
        else:
            result = "Rejected"
            reason = "Low CIBIL score, insufficient income or high loan amount."

        conn = get_db_connection()
        if conn is None:
            return "<h3>Database connection failed</h3>"

        cursor = conn.cursor()

        query = "INSERT INTO predictions (f1, f2, f3, f4, f5, f6, f7, f8, result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cursor.execute(query, (f1, f2, f3, f4, f5, f6, f7, f8, result))
        conn.commit()

        cursor.close()
        conn.close()

        return render_template("Result1.html",prediction=result,reason=reason)

    except Exception as e:
        return f"<h3>Error: {str(e)}</h3>"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)