"""
Admin authentication for single-user system.
Credentials stored in .env file.
"""

import os
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator to protect admin views.
    Redirects to login if not authenticated.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            messages.error(request, 'Please login to access admin panel')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def verify_admin_credentials(username: str, password: str) -> bool:
    """
    Verify admin credentials against .env file.
    
    Args:
        username: Username to verify
        password: Password to verify
    
    Returns:
        True if credentials match .env ADMIN_USERNAME and ADMIN_PASSWORD
    """
    stored_username = os.getenv('ADMIN_USERNAME', 'admin')
    stored_password = os.getenv('ADMIN_PASSWORD', 'Admin@1234')
    
    return username == stored_username and password == stored_password
