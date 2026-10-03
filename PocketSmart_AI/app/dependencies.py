from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def require_login(f):
    """
    Decorator to require login for a route.
    While Flask-Login provides @login_required, this serves as a demonstration
    of how dependencies might be adapted in a Flask architecture.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
