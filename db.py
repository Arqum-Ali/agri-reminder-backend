"""
Database connection module.
"""
import pymysql
import os
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

def get_db_connection():
    """
    Database se connect karne ka function – Railway pe crash nahi karega.
    """
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"[DB] Connected successfully to database '{DB_NAME}' with DictCursor.")
        return conn
    except Exception as e:
        print(f"[DB ERROR] Connection failed: {str(e)}")
        # Railway pe agar fail ho to None return kar – app crash nahi karega
        return None

def init_db():
    """
    Database initialize karne ka function – sirf local pe use kar.
    """
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database for initialization.")
        return False

    cursor = conn.cursor()

    try:
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE
            )
        """)

        # OTPS table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otps (
                id INT AUTO_INCREMENT PRIMARY KEY,
                phone VARCHAR(20) NOT NULL,
                otp_code VARCHAR(6) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Wheat listings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wheat_listings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                price_per_kg DECIMAL(10, 2) NOT NULL,
                quantity_kg DECIMAL(10, 2) NOT NULL,
                description TEXT NOT NOT NULL,
                wheat_variety VARCHAR(100),
                grade_quality VARCHAR(100),
                harvest_season VARCHAR(100),
                protein_content DECIMAL(4, 1),
                moisture_level DECIMAL(4, 1),
                organic_certified BOOLEAN DEFAULT FALSE,
                pesticides_used BOOLEAN DEFAULT FALSE,
                local_delivery_available BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Pesticide listings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pesticide_listings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                quantity DECIMAL(10, 2) NOT NULL,
                description TEXT NOT NULL,
                organic_certified BOOLEAN DEFAULT FALSE,
                restricted_use BOOLEAN DEFAULT FALSE,
                local_delivery_available BOOLEAN DEFAULT FALSE,
                product_image VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Crop reminders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crop_reminders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                crop_name VARCHAR(100) NOT NULL,
                planting_date DATE NOT NULL,
                field_name VARCHAR(100) NOT NULL,
                land_preparation_date DATE,
                seed_sowing_date DATE,
                first_irrigation_date DATE,
                second_irrigation_date DATE,
                urea_dose_date DATE,
                notified_first_irrigation BOOLEAN DEFAULT FALSE,
                notified_second_irrigation BOOLEAN DEFAULT FALSE,
                notified_urea_dose BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        print("All tables created successfully.")
        return True

    except Exception as e:
        print("Table creation failed:", e)
        return False

    finally:
        cursor.close()
        conn.close()