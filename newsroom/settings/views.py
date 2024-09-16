from inspect import iscoroutine
import re

from pydantic import BaseModel
from quart_babel import gettext

from superdesk.core.web import EndpointGroup, Request, Response
from superdesk.flask import render_template, g
from superdesk.utc import utcnow

from newsroom.core import get_current_wsgi_app
from newsroom.decorator import admin_only, account_manager_only
from newsroom.utils import get_json_or_400_async, set_version_creator

from .resource import update_settings_document


settings_endpoints = EndpointGroup("settings", __name__)


class SettingsAppRouteParams(BaseModel):
    app_id: str


@settings_endpoints.endpoint("/settings/<app_id>", methods=["GET"])
@account_manager_only
async def settings_app(args: SettingsAppRouteParams, params: None, request: Request):
    from newsroom.users import get_user_profile_data  # noqa

    user_profile_data = await get_user_profile_data()
    app = get_current_wsgi_app()

    for app in app.settings_apps:
        if app._id == args.app_id:
            value = app.data()
            data = await value if iscoroutine(value) else value
            return await render_template(
                "settings.html", setting_type=args.app_id, data=data, user_profile_data=user_profile_data
            )

    await request.abort(404)


@settings_endpoints.endpoint("/settings/general_settings", methods=["POST"])
@admin_only
async def update_values(request: Request):
    values = await get_json_or_400_async(request)

    error = validate_general_settings(values)
    if error:
        return "", error

    updates = {"values": values}
    set_version_creator(updates)
    updates["_updated"] = utcnow()

    update_settings_document(updates)
    g.settings = None  # reset cache on update
    return Response(updates)


def validate_general_settings(values):
    # validate email formats for company_expiry_alert_recipients
    email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    fields = [
        "company_expiry_alert_recipients",
        "coverage_request_recipients",
        "system_alerts_recipients",
        "product_seat_request_recipients",
    ]
    for field in fields:
        field_txt = (
            gettext("Company expiry alert recipients")
            if field == "company_expiry_alert_recipients"
            else gettext("Coverage request recipients")
        )

        for email in (values.get(field) or "").split(","):
            if email and not email_regex.match(email.strip()):
                return gettext("{}: Email IDs not in proper format".format(field_txt))
