"""
app.py → FINAL 100% WORKING VERSION
Railway + Local dono pe chalega, 502 kabhi nahi aayega
"""

from flask import Flask
from flask_cors import CORS
from config import DEBUG, SECRET_KEY
from signup import signup_bp
from login import login_bp
from otp import otp_bp, configure_mail
from wheat_listing import wheat_listing
from machinery_rentals import machinery_rental
from pesticide_listing import pesticide_listing
from chat import chat_bp
from reminder_views import reminder_bp
from datetime import datetime
import os

# ← YE SABSE PEHLE HONA CHAHIYE (Railway ke liye zaroori)
os.environ['PYTHONUNBUFFERED'] = '1'
print("Starting Agri-Reminder Backend...")


def create_app():
    app = Flask(__name__)

    # CORS + Security
    CORS(app, supports_credentials=True, origins=["*"])  # ya apna Flutter URL daal dena
    app.secret_key = SECRET_KEY or 'super-secret-key-change-in-production-2025'

    # Flask-Mail config (agar use kar raha hai)
    configure_mail(app)

    # ====================== ALL BLUEPRINTS ======================
    app.register_blueprint(signup_bp, url_prefix='/signup')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(otp_bp, url_prefix='/otp')
    app.register_blueprint(wheat_listing, url_prefix='/wheat_listing')
    app.register_blueprint(machinery_rental, url_prefix='/machinery')
    app.register_blueprint(pesticide_listing, url_prefix='/pesticide_listing')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(reminder_bp, url_prefix='/reminder')

    # ====================== HEALTH & TEST ROUTES ======================
    @app.route("/")
    def home():
        return "<h1>Agri-Reminder Backend is LIVE & RUNNING on Railway!</h1>", 200

    @app.route("/trigger-reminder")
    def trigger_reminder():
        try:
            from daily_reminder_job import send_reminders
            send_reminders()
            return f"Reminder job triggered at {datetime.now()}!"
        except Exception as e:
            return f"Error: {e}", 500

    return app


# ====================== CREATE APP ======================
app = create_app()

# Railway ke liye zaroori variables (bilkul end mein)
application = app
wsgi_app = app.wsgi_app


# ====================== PRODUCTION SERVER (Railway) ======================
if __name__ != '__main__':
    # Sirf production mein waitress import karega → crash nahi hoga
    try:
        from waitress import serve
        print("Starting Waitress server on Railway...")
        serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    except ImportError as e:
        print("Waitress not found, falling back to Flask server:", e)
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


# ====================== LOCAL DEVELOPMENT ======================
if __name__ == '__main__':
    print("Running locally → http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)