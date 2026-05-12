# security.py

from functools import wraps
from flask_login import current_user
from flask import abort

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if current_user.role not in roles:
                abort(403)

            return f(*args, **kwargs)
        return wrapper
    return decorator