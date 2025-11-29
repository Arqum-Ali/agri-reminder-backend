"""
Configuration settings for the application.
"""
import os

DB_HOST       = os.environ.get('MYSQLHOST')
DB_PORT       = int(os.environ.get('MYSQLPORT', 3306))
DB_USER       = os.environ.get('MYSQLUSER')
DB_PASSWORD   = os.environ.get('MYSQLPASSWORD')
DB_NAME       = os.environ.get('MYSQLDATABASE')
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