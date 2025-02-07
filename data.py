import streamlit as st
from auth import register_user, authenticate_user

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
