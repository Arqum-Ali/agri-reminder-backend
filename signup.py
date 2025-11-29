import random
import os
import requests
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from db import get_db_connection

signup_bp = Blueprint('signup', __name__)

# Resend credentials (Railway se lenge)
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')

# ===================== SEND EMAIL VIA RESEND (100% safe) =====================
def send_email_otp(recipient_email, otp_code):
    if not RESEND_API_KEY:
        print("RESEND_API_KEY not set – email skipped")
        return

    try:
        payload = {
            "from": f"Agri-Reminder <{FROM_EMAIL}>",
            "to": [recipient_email],
            "subject": "Your OTP Code",
            "html": f"""
                <h2>Your OTP is <b style="color:green;">{otp_code}</b></h2>
                <p>Valid for 10 minutes.</p>
            """
        }
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json=payload,
            timeout=10
        )
        if response.status_code in (200, 202):
            print(f"OTP sent to {recipient_email}")
        else:
            print("Resend error:", response.text)
    except Exception as e:
        print(f"Email error (ignored): {e}")  # ← crash nahi hoga


# ===================== SIGNUP =====================
@signup_bp.route('', methods=['POST'])
def signup():
    data = request.get_json()
    full_name = data.get('full_name')
    phone = data.get('phone')
    email = data.get('email')
    password = data.get('password')

    if not all([full_name, phone, email, password]):
        return jsonify({'error': 'All fields required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password too short'}), 400

    otp_code = str(random.randint(1000, 9999))
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database error'}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE phone=%s OR email=%s", (phone, email))
        if cursor.fetchone():
            return jsonify({'error': 'Already registered'}), 409

        hashed = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (full_name, phone, email, password_hash, email_otp, otp_attempts)
            VALUES (%s, %s, %s, %s, %s, 0)
        """, (full_name, phone, email, hashed, otp_code))
        conn.commit()
        user_id = cursor.lastrowid

        send_email_otp(email, otp_code)  # ← fail ho jaye to bhi signup pass

        return jsonify({
            'message': 'Signup successful! Check email for OTP.',
            'user_id': user_id,
            'debug_otp': otp_code  # testing ke liye — baad mein hata dena
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ===================== VERIFY OTP =====================
@signup_bp.route('/verifyotp', methods=['POST'])
def verifyotp():
    data = request.get_json()
    otp = data.get('otp')
    user_id = data.get('user_id')
    if not otp or not user_id:
        return jsonify({'error': 'OTP & user_id required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT email_otp, otp_attempts FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if str(user[0]) != str(otp):
            attempts = user[1] + 1
            cursor.execute("UPDATE users SET otp_attempts=%s WHERE id=%s", (attempts, user_id))
            conn.commit()
            if attempts >= 3:
                cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
                conn.commit()
                return jsonify({'error': 'Too many attempts'}), 400
            return jsonify({'error': 'Wrong OTP', 'left': 3-attempts}), 401

        cursor.execute("UPDATE users SET email_otp=NULL, otp_attempts=0 WHERE id=%s", (user_id,))
        conn.commit()
        return jsonify({'message': 'Account verified!'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()