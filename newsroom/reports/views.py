from pydantic import BaseModel
from inspect import isawaitable
from io import StringIO
import csv

from quart_babel import gettext

from superdesk.core import get_current_app, get_app_config
from superdesk.core.types import Request, Response
from superdesk.core.web import EndpointGroup
from superdesk.flask import render_template
from newsroom.auth import auth_rules
from newsroom.auth.utils import get_user_from_request
from newsroom.utils import query_resource

from .utils import get_current_user_reports
from newsroom.users import get_user_profile_data


class RouteArguments(BaseModel):
    report: str


blueprint = EndpointGroup("reports", __name__)


@blueprint.endpoint(
    "/reports/print/<string:report>", methods=["GET"], auth=[auth_rules.account_manager_or_company_admin_only]
)
async def print_reports(args: RouteArguments, params: None, request: Request):
    report = args.report
    if not report:
        return await request.abort(400, gettext("Report not specified"))

    reports = get_current_user_reports()
    func = reports.get(report)

    if not func:
        return await request.abort(400, gettext("Unknown report {}".format(report)))

    data = func()
    if isawaitable(data):
        data = await data
    return await render_template("reports_print.html", setting_type="print_reports", data=data, report=report)


@blueprint.endpoint(
    "/reports/company_reports", methods=["GET"], auth=[auth_rules.account_manager_or_company_admin_only]
)
async def company_reports(request: Request):
    companies = list(query_resource("companies"))
    user_profile_data = await get_user_profile_data()
    user = get_user_from_request(request)
    data = {
        "companies": companies,
        "sections": get_current_app().as_any().sections,
        "api_enabled": get_app_config("NEWS_API_ENABLED", False),
        "current_user_type": user.user_type,
    }
    return await render_template(
        "company_reports.html", setting_type="company_reports", data=data, user_profile_data=user_profile_data
    )


@blueprint.endpoint(
    "/reports/<string:report>", methods=["GET"], auth=[auth_rules.account_manager_or_company_admin_only]
)
async def get_report(args: RouteArguments, params: None, request: Request) -> Response:
    report = args.report
    if not report:
        return await request.abort(400, gettext("Report not specified"))

    reports = get_current_user_reports()
    func = reports.get(report)

    if not func:
        return await request.abort(400, gettext("Unknown report {}".format(report)))

    results = func()
    if isawaitable(results):
        results = await results
    return Response(results)


@blueprint.endpoint(
    "/reports/export/<string:report>", methods=["GET"], auth=[auth_rules.account_manager_or_company_admin_only]
)
async def export_reports(args: RouteArguments, params: None, request: Request):
    report = args.report
    if not report:
        return await request.abort(400, gettext("Report not specified"))

    reports = get_current_user_reports()
    func = reports.get(report)

    if not func:
        return await request.abort(400, gettext("Unknown report {}".format(report)))

    rows = func()
    if isawaitable(rows):
        rows = await rows
    data = StringIO()
    writer = csv.writer(data, dialect="excel")

    for row in rows:
        writer.writerow(row)

    csv_file = data.getvalue().encode("utf-8")

    response = get_current_app().response_class(response=csv_file, status=200, mimetype="text/csv")

    response.content_length = len(csv_file)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = 'attachment; filename="report-export.csv"'

    return response
