from flask import Flask, jsonify
from flask_cors import CORS
import os

# Ye 2 lines sabse pehle
os.environ['PYTHONUNBUFFERED'] = '1'
print("Starting backend...")

app = Flask(__name__)
CORS(app)  # Flutter ke liye

# Simple test route
@app.route("/")
def home():
    return "BHAI BACKEND LIVE HO GAYA — AB SAB CHALEGA!"

# Signup route (sirf test ke liye)
@app.route("/signup", methods=["POST"])
def signup():
    return jsonify({"message": "Signup working!", "status": "success"})

# Login route
@app.route("/login", methods=["POST"])
def login():
    return jsonify({"message": "Login working!", "status": "success"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)