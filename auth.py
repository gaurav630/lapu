import sqlite3
import hashlib

DB_PATH = "users.db"

# Hash function for password security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register new user
def register_user(username, password):
    hashed_pw = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

# Authenticate user login
def authenticate_user(username, password):
    hashed_pw = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    user = cursor.fetchone()
    
    conn.close()
    return user is not None
