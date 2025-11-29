import random
import os
import requests
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from db import get_db_connection



signup_bp = Blueprint('signup', __name__)

# ==================== ENV VARIABLES FROM RAILWAY ====================
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL     = os.getenv("FROM_EMAIL", "onboarding@resend.dev")


# ==================== SEND OTP VIA RESEND.COM ====================
def send_email_otp(recipient_email, otp_code):
    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY missing in Railway variables")
        return

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": f"Agriculture App <{FROM_EMAIL}>",
                "to": [recipient_email],
                "subject": "Your Verification OTP Code",
                "html": f"""
                    <div style="font-family: Arial; padding: 20px;">
                        <h2>Welcome!</h2>
                        <p>Your verification code is:</p>
                        <h1 style="color: green; letter-spacing: 5px;"><b>{otp_code}</b></h1>
                        <p>This code is valid for 10 minutes.</p>
                    </div>
                """
            },
            timeout=10
        )

        if response.status_code in (200, 202):
            print(f"✔ OTP Email sent to {recipient_email}")
        else:
            print("❌ Resend Error:", response.text)

    except Exception as e:
        print(f"❌ Resend failed: {e}")


# ==================== SIGNUP ROUTE ====================
@signup_bp.route('', methods=['POST'])
def signup():





    data = request.get_json()

    full_name = data.get('full_name')
    phone     = data.get('phone')
    email     = data.get('email')
    password  = data.get('password')

    if not all([full_name, phone, email, password]):
        return jsonify({'error': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    otp_code = str(random.randint(1000, 9999))

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        # Check existing user
        cursor.execute(
            "SELECT id FROM users WHERE phone = %s OR email = %s",
            (phone, email)
        )
        if cursor.fetchone():
            return jsonify({'error': 'Phone or email already registered'}), 409

        password_hash = generate_password_hash(password)

        # Insert new user
        cursor.execute("""
            INSERT INTO users (full_name, phone, email, password_hash, email_otp, otp_attempts)
            VALUES (%s, %s, %s, %s, %s, 0)
        """, (full_name, phone, email, password_hash, otp_code))

        conn.commit()
        user_id = cursor.lastrowid

        # Send OTP Email (non-blocking)
        send_email_otp(email, otp_code)

        return jsonify({
            'message': 'Signup successful! OTP sent to email.',
            'user_id': user_id,
            'debug_otp': otp_code    # REMOVE IN PRODUCTION
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ==================== VERIFY OTP ROUTE ====================
@signup_bp.route('/verifyotp', methods=['POST'])
def verifyotp():




    data = request.get_json()

    otp_code = data.get('otp')
    user_id  = data.get('user_id')

    if not otp_code or not user_id:
        return jsonify({'error': 'OTP + user_id required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT email_otp, otp_attempts FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:



            
            return jsonify({'error': 'User not found'}), 404

        if str(user['email_otp']) != str(otp_code):
            attempts = user['otp_attempts'] + 1

            cursor.execute("UPDATE users SET otp_attempts = %s WHERE id = %s", (attempts, user_id))
            conn.commit()

            if attempts >= 3:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                return jsonify({'error': 'Too many attempts. Register again.'}), 400

            return jsonify({
                'error': 'Incorrect OTP',
                'attempts_left': 3 - attempts
            }), 401

        # Correct OTP
        cursor.execute("""
            UPDATE users
            SET email_otp = NULL, otp_attempts = 0
            WHERE id = %s
        """, (user_id,))
        conn.commit()

        return jsonify({'message': 'OTP verified. Account activated!'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()
