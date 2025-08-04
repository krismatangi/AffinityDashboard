import os
import hashlib
from functools import wraps
from flask import request, session, redirect, url_for, flash

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_auth(username, password):
    """Check if username/password combination is valid"""
    # Get credentials from environment variables
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Hash the provided password
    hashed_password = hash_password(password)
    expected_hash = hash_password(admin_password)
    
    return username == admin_username and hashed_password == expected_hash

def requires_auth(f):
    """Decorator that requires authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access admin features', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def login_user(username, password):
    """Login user and set session"""
    if check_auth(username, password):
        session['logged_in'] = True
        session['admin_username'] = username
        return True
    return False

def logout_user():
    """Logout user and clear session"""
    session.pop('logged_in', None)
    session.pop('admin_username', None)