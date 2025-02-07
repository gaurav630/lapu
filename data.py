import streamlit as st
import sqlite3
import subprocess
from auth import authenticate_user

DB_PATH = "users.db"

def register_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False  # Username already taken
    
    # Insert new user
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    
    # Commit and push changes to GitHub
    commit_and_push_changes()
    
    return True

def commit_and_push_changes():
    try:
        subprocess.run(["git", "add", DB_PATH], check=True)
        subprocess.run(["git", "commit", "-m", "Update users.db with new signup"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)  # Change 'main' if needed
    except Exception as e:
        print(f"Git commit/push failed: {e}")

# Streamlit UI
st.title("Login System with SQLite")

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login":
    st.subheader("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid credentials, try again.")

elif choice == "Sign Up":
    st.subheader("Create an Account")
    
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    
    if st.button("Sign Up"):
        if register_user(new_username, new_password):
            st.success("Account created successfully! You can now log in.")
        else:
            st.warning("Username already taken, choose another.")
