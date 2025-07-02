from functools import wraps
from flask import request, session, redirect, url_for, flash
import hashlib
import os

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_auth(username, password):
    """Check if username/password combination is valid"""
    # Get credentials from environment variables
    valid_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "!Aff1n1ty#")
    valid_password_hash = hash_password(admin_password)
    
    return username == valid_username and hash_password(password) == valid_password_hash

def authenticate():
    """Send a 401 response that enables basic auth"""
    return redirect(url_for('login'))

def requires_auth(f):
    """Decorator that requires authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def login_user(username, password):
    """Login user and set session"""
    if check_auth(username, password):
        session['authenticated'] = True
        session['username'] = username
        return True
    return False

def logout_user():
    """Logout user and clear session"""
    session.pop('authenticated', None)
    session.pop('username', None)