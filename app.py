"""
Main application entry point – 100% Railway + Local working (FINAL FIXED)
"""
from flask import Flask
from flask_cors import CORS
from config import DEBUG
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

# ← YE 2 LINES TOP PE HI ADD KAR DE (sabse pehle)
os.environ['PYTHONUNBUFFERED'] = '1'
print("Agri-Reminder Backend Starting...")

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True, origins=["*"])  # ← * ya apna Flutter URL daal dena
    app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key-2025-change-this')

    # Mail config (agar Flask-Mail use kar raha hai)
    configure_mail(app)

    # Register Blueprints
    app.register_blueprint(signup_bp, url_prefix='/signup')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(otp_bp, url_prefix='/otp')
    app.register_blueprint(wheat_listing, url_prefix='/wheat_listing')
    app.register_blueprint(machinery_rental, url_prefix='/machinery')
    app.register_blueprint(pesticide_listing, url_prefix='/pesticide_listing')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(reminder_bp, url_prefix='/reminder')

    # Manual reminder trigger
    @app.route("/trigger-reminder")
    def trigger_reminder():
        from daily_reminder_job import send_reminders
        send_reminders()
        return f"Reminder triggered at {datetime.now()}!"

    # Health check route
    @app.route("/")
    def home():
        return "Agri-Reminder Backend is LIVE on Railway!"

    return app

# ──────────────────────── MAIN APP ────────────────────────
app = create_app()

# Railway ke liye zaroori hai (ye 3 lines bilkul end mein hone chahiye)
application = app
wsgi_app = app.wsgi_app

if __name__ == '__main__':
    print("Running locally → http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)
else:
    # Production (Railway) – Waitress server
    print("Starting Waitress server on Railway...")
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))