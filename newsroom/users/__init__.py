import superdesk

from flask import Blueprint
from flask_babel import lazy_gettext


from .users import AuthUserService, UsersResource, AuthUserResource, users_service

blueprint = Blueprint("users", __name__)


def init_app(app):
    superdesk.register_resource("users", UsersResource, service_instance=users_service, _app=app)
    superdesk.register_resource("auth_user", AuthUserResource, AuthUserService, _app=app)
    from . import views  # noqa

    app.settings_app(
        "users",
        lazy_gettext("User Management"),
        weight=200,
        data=views.get_settings_data,
        allow_account_mgr=True,
    )


async def get_user_profile_data():
    from . import views  # noqa

    data = await views.get_view_data()
    return data
