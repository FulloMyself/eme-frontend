import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eme_cv_bot.db')

def get_db_connection():
    """Get a database connection with row factory set"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                professional_summary TEXT,
                skills TEXT,
                languages TEXT,
                doc_id_path TEXT,
                doc_proof_path TEXT,
                cv_path TEXT,
                submission_date TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Work experience table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                job_title TEXT,
                company TEXT,
                start_date TEXT,
                end_date TEXT,
                responsibilities TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Education table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS education (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                degree TEXT,
                institution TEXT,
                graduation_year TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Certifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                cert_name TEXT,
                issuer TEXT,
                year TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")
        raise
    finally:
        conn.close()

def get_all_users():
    """Get all users from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY submission_date DESC')
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    """Get a specific user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_experience(user_id):
    """Get work experience for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM work_experience WHERE user_id = ?', (user_id,))
    experience = cursor.fetchall()
    conn.close()
    return experience

def get_user_education(user_id):
    """Get education for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM education WHERE user_id = ?', (user_id,))
    education = cursor.fetchall()
    conn.close()
    return education

def get_user_certifications(user_id):
    """Get certifications for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM certifications WHERE user_id = ?', (user_id,))
    certifications = cursor.fetchall()
    conn.close()
    return certifications