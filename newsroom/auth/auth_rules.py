from quart_babel import gettext

from superdesk.core.types import Request, HTTP_METHOD, AuthRule

from newsroom.types import UserRole
from newsroom.exceptions import AuthorizationError


def user_role_required(roles: list[str] | dict[HTTP_METHOD, list[str]] | str) -> AuthRule:
    user_roles: list[str] | dict[HTTP_METHOD, list[str]] = roles if not isinstance(roles, str) else [roles]

    async def run_rule(request: Request) -> None:
        from .utils import get_user_from_request

        expected_roles = user_roles.get(request.method) if isinstance(user_roles, dict) else user_roles
        if not expected_roles:
            return

        user = get_user_from_request(request)
        if user.user_type != UserRole.ADMINISTRATOR and user.user_type not in expected_roles:
            raise AuthorizationError(
                403,
                gettext("The requested resource is not available for your subscription."),
                title=gettext("403. Forbidden"),
            )

    return run_rule


admin_only = user_role_required([UserRole.ADMINISTRATOR])
account_manager_only = user_role_required([UserRole.ACCOUNT_MANAGEMENT])
company_admin_only = user_role_required([UserRole.COMPANY_ADMIN])
account_manager_or_company_admin_only = user_role_required([UserRole.ACCOUNT_MANAGEMENT, UserRole.COMPANY_ADMIN])
any_user_role = user_role_required([role for role in UserRole])


def section_required(section: str) -> AuthRule:
    async def run_rule(request: Request) -> None:
        from .utils import get_current_user_sections

        if not get_current_user_sections(request).get(section):
            raise AuthorizationError(
                403, gettext("This page is not available for your subscription."), title=gettext("403. Forbidden")
            )

    return run_rule


def url_arg_must_be_current_user(arg_name: str) -> AuthRule:
    async def run_rule(request: Request) -> None:
        from .utils import get_user_from_request

        expected_id = get_user_from_request(request).id
        provided_id = request.get_view_args(arg_name)

        if str(expected_id) != str(provided_id):
            raise AuthorizationError(403, gettext("Unauthorized to edit another user"), title=gettext("403. Forbidden"))

    return run_rule
