from superdesk import get_resource_service

from newsroom.auth import get_user_by_email
from .manager import manager


def sanitize_user_data(user_data):
    return {k: v for k, v in user_data.items() if k != "password"}

@manager.command
def create_user(email, password, first_name, last_name, is_admin):
    """Create a user with given email, password, first_name, last_name and is_admin flag.

    If user with given username exists it's noop.

    Example:
    ::

        $ python manage.py create_user admin@admin.com adminadmin admin admin True

    """

    new_user = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "user_type": "administrator" if is_admin else "public",
        "is_enabled": True,
        "is_approved": True,
    }

    user = get_user_by_email(email)

    if user:
        sanitized_user = sanitize_user_data(new_user)
        print("user already exists %s" % str(sanitized_user))
    else:
        sanitized_user = sanitize_user_data(new_user)
        print("creating user %s" % str(sanitized_user))
        get_resource_service("users").post([new_user])
        print("user saved %s" % str(sanitized_user))

    return new_user
