import superdesk

from quart_babel import lazy_gettext
from inspect import iscoroutine

from .users import AuthUserService, UsersResource, AuthUserResource, users_service
from .service import UsersService, UsersAuthService
from .module import module  # noqa

__all__ = ["UsersService", "UsersAuthService"]


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

    func = views.get_view_data()
    data = await func if iscoroutine(func) else func
    return data
