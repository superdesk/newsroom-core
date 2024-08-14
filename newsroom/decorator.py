from functools import wraps

from superdesk.flask import request, redirect, url_for, abort, session
from newsroom.auth import get_user_required
from newsroom.auth.utils import (
    clear_user_session,
    is_current_user_account_mgr,
    is_current_user_admin,
    is_current_user_company_admin,
    is_valid_session,
    user_has_section_allowed,
)


def clear_session_and_redirect_to_login():
    clear_user_session()
    session["next_url"] = request.url
    return redirect(url_for("auth.login"))


def login_required(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return clear_session_and_redirect_to_login()
        return await f(*args, **kwargs)

    return async_decorated_function


def admin_only(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return clear_session_and_redirect_to_login()
        elif not is_current_user_admin():
            return abort(403)
        return await f(*args, **kwargs)

    return async_decorated_function


def account_manager_only(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return clear_session_and_redirect_to_login()
        elif not is_current_user_admin() and not is_current_user_account_mgr():
            return abort(403)
        return await f(*args, **kwargs)

    return async_decorated_function


def company_admin_only(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return clear_session_and_redirect_to_login()
        elif not is_current_user_company_admin():
            return abort(403)
        return await f(*args, **kwargs)

    return async_decorated_function


def account_manager_or_company_admin_only(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return clear_session_and_redirect_to_login()
        elif not is_current_user_admin() and not is_current_user_account_mgr() and not is_current_user_company_admin():
            return abort(403)
        return await f(*args, **kwargs)

    return async_decorated_function


def section(section):
    def _section_required(f):
        @wraps(f)
        async def async_wrapper(*args, **kwargs):
            user = get_user_required()
            if not is_current_user_admin() and not user_has_section_allowed(user, section):
                return abort(403)
            return await f(*args, **kwargs)

        return async_wrapper

    return _section_required
