from functools import wraps

from superdesk.flask import request, redirect, url_for, abort, session
from newsroom.auth.utils import get_user_from_request, get_current_user_sections, is_valid_session


# TODO-ASYNC: Remove this once everything is async
def redirect_to_login():
    session["next_url"] = request.url
    return redirect(url_for("auth.login"))


# TODO-ASYNC: Remove this once everything is async
def login_required(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return redirect_to_login()
        return await f(*args, **kwargs)

    return async_decorated_function


# TODO-ASYNC: Remove this once everything is async
def admin_only(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return redirect_to_login()
        user = get_user_from_request(None)
        if not user.is_admin():
            return abort(403)
        return await f(*args, **kwargs)

    return async_decorated_function


# TODO-ASYNC: Remove this once everything is async
def account_manager_only(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return redirect_to_login()
        user = get_user_from_request(None)
        if not user.is_admin() and not user.is_account_manager():
            return abort(403)
        return await f(*args, **kwargs)

    return async_decorated_function


# TODO-ASYNC: Remove this once everything is async
def company_admin_only(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return redirect_to_login()
        user = get_user_from_request(None)
        if not user.is_company_admin():
            return abort(403)
        return await f(*args, **kwargs)

    return async_decorated_function


# TODO-ASYNC: Remove this once everything is async
def account_manager_or_company_admin_only(f):
    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            return redirect_to_login()
        user = get_user_from_request(None)
        if not user.is_admin() and not user.is_account_manager() and not user.is_company_admin():
            return abort(403)

        return await f(*args, **kwargs)

    return async_decorated_function


# TODO-ASYNC: Remove this once everything is async
def section(section):
    def _section_required(f):
        @wraps(f)
        async def async_wrapper(*args, **kwargs):
            if not get_current_user_sections(None).get(section):
                return abort(403)
            return await f(*args, **kwargs)

        return async_wrapper

    return _section_required
