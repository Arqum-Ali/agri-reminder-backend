import os

# ========= DATABASE (Railway MySQL) =========
DB_HOST       = os.environ.get('MYSQLHOST')
DB_PORT       = int(os.environ.get('MYSQLPORT', 3306))
DB_USER       = os.environ.get('MYSQLUSER')
DB_PASSWORD   = os.environ.get('MYSQLPASSWORD')
DB_NAME       = os.environ.get('MYSQLDATABASE')

# ========= RESEND.COM (Email 100% jayegi) =========
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
FROM_EMAIL     = os.environ.get('FROM_EMAIL', 'onboarding@resend.dev')

# ========= APP =========
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'my-super-secret-key-2025')