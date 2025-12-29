import streamlit as st
import bcrypt

# Hardcoded Admin (In production, load this from Firestore)
ADMIN_USER = "admin"
# Hash for 'abc':
ADMIN_HASH = b'$2b$12$eX.N.xQ... (This is a placeholder, code will generate real hash)'

def check_login():
    # 1. Init Session State
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # 2. Check if already logged in
    if st.session_state.authenticated:
        return True, st.session_state.username, "KAIROS-HQ", "Admin", None

    # 3. Show Login Form
    st.markdown("## 🔐 KAIROS Clinical Login")
    
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            # Simple check for the demo
            if username == "admin" and password == "abc":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    
    # 4. Block App if not logged in
    if not st.session_state.authenticated:
        st.stop()
