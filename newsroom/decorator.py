from functools import wraps
from flask import request, redirect, url_for, abort
from newsroom.auth.utils import (
    clear_user_session,
    is_current_user_account_mgr,
    is_current_user_admin,
    is_valid_session,
)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_valid_session():
            clear_user_session()
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_current_user_admin() or not is_valid_session():
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


def account_manager_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_current_user_admin() and not is_current_user_account_mgr() or not is_valid_session():
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function
