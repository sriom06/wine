from flask import Flask, request, jsonify
import pandas as pd
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

FILE_NAME = "users.xlsx"

# Initialize Excel file if not exists
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["email", "password"])
    df.to_excel(FILE_NAME, index=False)

# Function to read user data
def read_users():
    return pd.read_excel(FILE_NAME)

# Function to save user data
def save_user(email, hashed_password):
    df = read_users()
    df = df.append({"email": email, "password": hashed_password}, ignore_index=True)
    df.to_excel(FILE_NAME, index=False)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data["email"]
    password = data["password"]

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    df = read_users()
    if email in df["email"].values:
        return jsonify({"message": "User already exists"}), 400

    # Hash password before saving
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    save_user(email, hashed_password)

    return jsonify({"message": "Signup successful!"}), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    df = read_users()
    user = df[df["email"] == email]

    if user.empty:
        return jsonify({"message": "User not found"}), 400

    stored_password = user["password"].values[0]

    if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Incorrect password"}), 400

if __name__ == "__main__":
    app.run(debug=True)
