from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for


def roles_required(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in role_names:
                flash("У вас недостаточно прав для выполнения данного действия", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
