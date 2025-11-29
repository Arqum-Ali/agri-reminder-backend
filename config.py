"""
config.py – FINAL VERSION (Railway + Gmail App Password ke liye perfect)
"""
import os

# ========= DATABASE =========
DB_HOST       = os.environ.get('MYSQLHOST')
DB_PORT       = int(os.environ.get('MYSQLPORT', 3306))
DB_USER       = os.environ.get('MYSQLUSER')
DB_PASSWORD   = os.environ.get('MYSQLPASSWORD')
DB_NAME       = os.environ.get('MYSQLDATABASE')

# ========= EMAIL (Railway ke liye safe tareeka) =========
MAIL_SERVER       = 'smtp.gmail.com'
MAIL_PORT         = 587
MAIL_USE_TLS      = True
MAIL_USE_SSL      = False
MAIL_USERNAME     = os.environ.get('MAIL_USERNAME')      # ← ab Railway se lega
MAIL_PASSWORD     = os.environ.get('MAIL_PASSWORD')      # ← ab Railway se lega (hard-code nahi)
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

# Debug ke liye
DEBUG = True

# Flask-Mail
from flask_mail import Mail
mail = Mail()