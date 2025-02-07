import streamlit as st
import sqlite3
import bcrypt
import jwt
import datetime
import pandas as pd
from contextlib import contextmanager

# ✅ Ensure `set_page_config` is the very first command
st.set_page_config(page_title="User Management", page_icon="👤", layout="wide")

# Database Path & Secret Key
DB_PATH = "users.db"
SECRET_KEY = "your-secret-key"

# Custom CSS for Styling
st.markdown("""
    <style>
        body {background-color: #f4f4f4;}
        .main {background: white; padding: 2rem; border-radius: 10px; box-shadow: 2px 2px 20px rgba(0,0,0,0.1);}
        .stTextInput, .stSelectbox, .stButton>button {
            border-radius: 10px !important;
            padding: 10px !important;
        }
        .stButton>button {
            background-color: #4CAF50 !important;
            color: white !important;
            font-size: 16px !important;
        }
        .stButton>button:hover {
            background-color: #45a049 !important;
        }
        .sidebar .sidebar-content {
            background: #262730;
            color: white;
        }
        .stSidebarContent {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Database Connection Manager
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

# Initialize Database
def init_database():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        conn.commit()

# Create Root User
def init_root_user():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", ("root",))
        if not cursor.fetchone():
            hashed_password = bcrypt.hashpw("root123".encode(), bcrypt.gensalt()).decode()
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", 
                           ("root", "root@admin.com", hashed_password, "Root"))
            conn.commit()

# Hash Password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify Password
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# Create JWT Token
def create_token(username):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    return jwt.encode({'username': username, 'exp': expiry}, SECRET_KEY, algorithm='HS256')

# Authenticate User
def authenticate_user(username, password):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and verify_password(password, result[0]):
            return True, create_token(username), result[1]
    return False, None, None

# Get All Users
def get_all_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, role FROM users")
        return cursor.fetchall()

# Add New User
def add_user(username, email, password, role):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return False, "Email already in use."
        
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", 
                       (username, email, hashed_password, role))
        conn.commit()
        return True, "User registered successfully."

# Reset Password
def reset_password(username, new_password):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", 
                           (hash_password(new_password), username))
            conn.commit()
            return True, "Password reset successfully."
    return False, "User not found."

# Initialize Database & Root User
init_database()
init_root_user()

# Sidebar Profile Section
if "current_user" in st.session_state:
    with st.sidebar:
        st.markdown(f"<h3 style='text-align: center;'>👤 {st.session_state['current_user']}</h3>", unsafe_allow_html=True)
        st.write(f"**Role:** {st.session_state['current_role']}")
        if st.button("Logout", key="logout"):
            st.session_state.clear()
            st.rerun()

st.title("🔐 Secure Login & User Management")

menu = ["🔑 Login", "🆕 Sign Up", "🔧 Admin Panel", "🔑 Forgot Password"]
choice = st.sidebar.radio("Menu", menu)

# Login Page
if choice == "🔑 Login":
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    st.subheader("🔓 Login")
    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if st.button("Login"):
        success, token, role = authenticate_user(username, password)
        if success:
            st.success(f"✅ Welcome {username}! Role: {role}")
            st.session_state["auth_token"] = token
            st.session_state["current_user"] = username
            st.session_state["current_role"] = role
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.markdown("</div>", unsafe_allow_html=True)

# Sign-Up
elif choice == "🆕 Sign Up":
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    st.subheader("📝 Create Account")
    username = st.text_input("👤 Username")
    email = st.text_input("📧 Email")
    password = st.text_input("🔒 Password", type="password")
    role = st.selectbox("Select Role", ["User", "Viewer"])

    if st.button("Sign Up"):
        success, message = add_user(username, email, password, role)
        if success:
            st.success(message)
        else:
            st.error(message)
    st.markdown("</div>", unsafe_allow_html=True)

# Admin Panel (Only for Root)
elif choice == "🔧 Admin Panel":
    if st.session_state.get("current_role") != "Root":
        st.warning("⚠️ Only Root can access this panel")
    else:
        st.subheader("🔧 Manage Users")
        users = pd.DataFrame(get_all_users(), columns=["Username", "Email", "Role"])
        st.dataframe(users)

# Forgot Password
elif choice == "🔑 Forgot Password":
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    st.subheader("🔑 Reset Your Password")
    username = st.text_input("Enter Your Username")
    new_password = st.text_input("Enter New Password", type="password")
    if st.button("Reset Password"):
        success, message = reset_password(username, new_password)
        if success:
            st.success(message)
        else:
            st.error(message)
    st.markdown("</div>", unsafe_allow_html=True)
