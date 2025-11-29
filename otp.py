import random
import os
import smtplib
from email.mime.text import MIMEText
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from db import get_db_connection

signup_bp = Blueprint('signup', __name__)

# ==================== EMAIL FUNCTION (Railway pe 100% chalega) ====================
def send_email_otp(recipient_email, otp_code):
    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')

    # Agar Railway pe variables nahi mile to skip kar de (signup fail nahi hoga)
    if not sender_email or not sender_password:
        print("MAIL_USERNAME or MAIL_PASSWORD not set – skipping email")
        return

    try:
        msg = MIMEText(f"""
Hello!

Welcome to Agri-Reminder App

Your verification OTP is: {otp_code}

Valid for 10 minutes only.
Do not share this OTP with anyone.

Thank you!
Team Agri-Reminder
        """.strip())

        msg['Subject'] = 'Agri-Reminder – Your OTP Code'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Port 587 + TLS → Railway pe best kaam karta hai
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=20) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"OTP email successfully sent to {recipient_email}")
    except Exception as e:
        print(f"Email sending failed (but signup continues): {e}")
        # Email fail ho jaye to bhi user register ho jayega
        pass


# ==================== SIGNUP ROUTE ====================
@signup_bp.route('', methods=['POST'])
def signup():
    data = request.get_json()
    full_name = data.get('full_name')
    phone = data.get('phone')
    email = data.get('email')
    password = data.get('password')

    if not all([full_name, phone, email, password]):
        return jsonify({'error': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    email_otp = str(random.randint(1000, 9999))

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()

    try:
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE phone = %s OR email = %s", (phone, email))
        if cursor.fetchone():
            return jsonify({'error': 'Phone or email already registered'}), 409

        password_hash = generate_password_hash(password)

        # Insert new user
        cursor.execute("""
            INSERT INTO users (full_name, phone, email, password_hash, email_otp, otp_attempts)
            VALUES (%s, %s, %s, %s, %s, 0)
        """, (full_name, phone, email, password_hash, email_otp))

        conn.commit()
        user_id = cursor.lastrowid

        # Send OTP email (fail hone pe bhi signup pass rahega)
        send_email_otp(email, email_otp)

        return jsonify({
            'message': 'User registered successfully! OTP sent to your email.',
            'user_id': user_id,
            'debug_otp': email_otp  # sirf testing ke liye – baad mein hata dena
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

    finally:
        cursor.close()
        conn.close()


# ==================== VERIFY OTP ROUTE ====================
@signup_bp.route('/verifyotp', methods=['POST'])
def verifyotp():
    data = request.get_json()
    otp_code = data.get('otp')
    user_id = data.get('user_id')

    if not otp_code or not user_id:
        return jsonify({'error': 'OTP and user_id are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT email_otp, otp_attempts FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        stored_otp = user['email_otp']
        attempts = user['otp_attempts'] or 0

        if str(stored_otp) != str(otp_code):
            attempts += 1
            cursor.execute("UPDATE users SET otp_attempts = %s WHERE id = %s", (attempts, user_id))
            conn.commit()

            if attempts >= 3:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                return jsonify({'error': 'Too many wrong attempts. Please register again.'}), 400

            return jsonify({'error': 'Invalid OTP', 'attempts_left': 3 - attempts}), 401

        # OTP correct
        cursor.execute("UPDATE users SET email_otp = NULL, otp_attempts = 0 WHERE id = %s", (user_id,))
        conn.commit()

        return jsonify({'message': 'OTP verified! Account activated successfully.'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500

    finally:
        cursor.close()
        conn.close()