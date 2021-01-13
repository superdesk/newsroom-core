from superdesk import get_resource_service

from newsroom.auth import get_user_by_email
from .manager import app, manager


@manager.command
def create_user(email, password, first_name, last_name, is_admin):
    """Create a user with given email, password, first_name, last_name and is_admin flag.

    If user with given username exists it's noop.

    Example:
    ::

        $ python manage.py create_user admin@admin.com adminadmin admin admin True

    """

    new_user = {
        'email': email,
        'password': password,
        'first_name': first_name,
        'last_name': last_name,
        'user_type': 'administrator' if is_admin else 'public',
        'is_enabled': True,
        'is_approved': True
    }

    with app.test_request_context('/users', method='POST'):

        user = get_user_by_email(email)

        if user:
            print('user already exists %s' % str(new_user))
        else:
            print('creating user %s' % str(new_user))
            get_resource_service('users').post([new_user])
            print('user saved %s' % (new_user))

        return new_user
