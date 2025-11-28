"""
Configuration settings for the application.
"""
import os

# Database Configuration (Railway aur local dono ke liye safe)
DB_USER = os.environ.get('MYSQLUSER', 'root')
DB_PASSWORD = os.environ.get('MYSQLPASSWORD', '1234')
DB_HOST = os.environ.get('MYSQLHOST', 'localhost')
DB_NAME = os.environ.get('MYSQLDATABASE', 'agrox_fyp')

# Application Configuration
DEBUG = True

# Mail Configuration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'arhumdoger@gmail.com'
MAIL_PASSWORD = 'auyb ccul xphy wpwh'  # agar expire ho gaya to naya bana lena
MAIL_DEFAULT_SENDER = 'arhumdoger@gmail.com'

# Flask-Mail instance
from flask_mail import Mail
mail = Mail()