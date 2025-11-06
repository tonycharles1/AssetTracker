"""
Authentication Module
"""
import streamlit as st
import hashlib
from google_sheets import GoogleSheetsDB
from config import SESSION_KEYS, SHEETS

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(db, username, password):
    """Authenticate user credentials"""
    try:
        users_df = db.read_data(SHEETS['users'])
        if users_df.empty:
            return None
        
        hashed_password = hash_password(password)
        user = users_df[
            (users_df['Username'].str.lower() == username.lower()) &
            (users_df['Password'] == hashed_password)
        ]
        
        if not user.empty:
            return {
                'username': user.iloc[0]['Username'],
                'role': user.iloc[0].get('Role', 'User'),
                'user_id': user.iloc[0].get('ID', '')
            }
        return None
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None

def register_user(db, username, password, role='User'):
    """Register a new user"""
    try:
        users_df = db.read_data(SHEETS['users'])
        
        # Check if username already exists
        if not users_df.empty:
            if username.lower() in users_df['Username'].str.lower().values:
                return False, "Username already exists"
        
        # Create new user record
        hashed_password = hash_password(password)
        new_user = {
            'Username': username,
            'Password': hashed_password,
            'Role': role,
            'CreatedAt': str(st.session_state.get('current_time', ''))
        }
        
        # Get next ID
        if users_df.empty:
            new_user['ID'] = '1'
        else:
            max_id = users_df['ID'].astype(int).max() if 'ID' in users_df.columns else 0
            new_user['ID'] = str(max_id + 1)
        
        db.append_row(SHEETS['users'], new_user)
        return True, "User registered successfully"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get(SESSION_KEYS['authenticated'], False)

def get_current_user():
    """Get current user information"""
    if check_authentication():
        return {
            'username': st.session_state.get(SESSION_KEYS['username'], ''),
            'role': st.session_state.get(SESSION_KEYS['user_role'], 'User'),
            'user_id': st.session_state.get(SESSION_KEYS['user_id'], '')
        }
    return None

def logout():
    """Logout current user"""
    for key in SESSION_KEYS.values():
        if key in st.session_state:
            del st.session_state[key]

