from io import StringIO
import csv

from quart_babel import gettext

from superdesk.core import get_current_app, get_app_config
from superdesk.flask import session, jsonify, render_template, abort
from newsroom.decorator import account_manager_or_company_admin_only
from newsroom.reports import blueprint
from newsroom.utils import query_resource

from .utils import get_current_user_reports
from newsroom.users import get_user_profile_data


@blueprint.route("/reports/print/<report>", methods=["GET"])
@account_manager_or_company_admin_only
async def print_reports(report):
    reports = get_current_user_reports()
    func = reports.get(report)

    if not func:
        abort(400, gettext("Unknown report {}".format(report)))

    data = func()
    return await render_template("reports_print.html", setting_type="print_reports", data=data, report=report)


@blueprint.route("/reports/company_reports", methods=["GET"])
@account_manager_or_company_admin_only
async def company_reports():
    companies = list(query_resource("companies"))
    user_profile_data = await get_user_profile_data()
    data = {
        "companies": companies,
        "sections": get_current_app().as_any().sections,
        "api_enabled": get_app_config("NEWS_API_ENABLED", False),
        "current_user_type": session.get("user_type"),
    }
    return await render_template(
        "company_reports.html", setting_type="company_reports", data=data, user_profile_data=user_profile_data
    )


@blueprint.route("/reports/<report>", methods=["GET"])
@account_manager_or_company_admin_only
async def get_report(report):
    reports = get_current_user_reports()
    func = reports.get(report)

    if not func:
        abort(400, gettext("Unknown report {}".format(report)))

    results = func()
    return jsonify(results), 200


@blueprint.route("/reports/export/<report>", methods=["GET"])
@account_manager_or_company_admin_only
async def export_reports(report):
    reports = get_current_user_reports()
    func = reports.get(report)

    if not func:
        abort(400, gettext("Unknown report {}".format(report)))

    rows = func()
    data = StringIO()
    writer = csv.writer(data, dialect="excel")

    for row in rows:
        writer.writerow(row)

    csv_file = data.getvalue().encode("utf-8")

    response = get_current_app().response_class(
        response=csv_file, status=200, mimetype="text/csv", direct_passthrough=True
    )

    response.content_length = len(csv_file)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = 'attachment; filename="report-export.csv"'

    return response
