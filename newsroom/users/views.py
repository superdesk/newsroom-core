import re

import flask
from bson import ObjectId
from flask import jsonify, current_app as app
from flask_babel import gettext
from superdesk import get_resource_service
from werkzeug.exceptions import BadRequest, NotFound

from newsroom.user_roles import UserRole
from newsroom.auth import get_user, get_user_by_email, get_company
from newsroom.auth.utils import (
    send_token,
    add_token_data,
    is_current_user_admin,
    is_current_user,
    is_current_user_account_mgr,
    is_current_user_company_admin,
)
from newsroom.decorator import admin_only, login_required, account_manager_or_company_admin_only
from newsroom.companies import (
    get_user_company_name,
    get_company_sections_monitoring_data,
)
from newsroom.notifications.notifications import get_notifications_with_items
from newsroom.notifications import push_user_notification, push_company_notification
from newsroom.topics import get_user_topics
from newsroom.users import blueprint
from newsroom.users.forms import UserForm
from newsroom.users.users import COMPANY_ADMIN_ALLOWED_UPDATES, NON_ADMIN_ALLOWED_UPDATES
from newsroom.utils import query_resource, find_one, get_json_or_400, get_vocabulary
from newsroom.monitoring.views import get_monitoring_for_company


def get_settings_data():
    return {
        "users": list(query_resource("users")),
        "companies": list(query_resource("companies")),
        "sections": app.sections,
        "products": list(query_resource("products")),
    }


def get_view_data():
    user = get_user()
    company = user["company"] if user and user.get("company") else None
    rv = {
        "user": user if user else None,
        "company": str(company),
        "topics": get_user_topics(user["_id"]) if user else [],
        "companyName": get_user_company_name(user),
        "locators": get_vocabulary("locators"),
        "monitoring_list": get_monitoring_for_company(user),
        "ui_configs": {config["_id"]: config for config in query_resource("ui_config")},
        "groups": app.config.get("WIRE_GROUPS", []),
    }

    if app.config.get("ENABLE_MONITORING"):
        rv["monitoring_list"] = get_monitoring_for_company(user)

    rv.update(get_company_sections_monitoring_data(company))

    return rv


@blueprint.route("/myprofile", methods=["GET"])
@login_required
def user_profile():
    return flask.render_template("user_profile.html", data=get_view_data())


@blueprint.route("/users/search", methods=["GET"])
@account_manager_or_company_admin_only
def search():
    lookup = None
    if flask.request.args.get("q"):
        regex = re.compile(".*{}.*".format(flask.request.args.get("q")), re.IGNORECASE)
        lookup = {"$or": [{"first_name": regex}, {"last_name": regex}]}

    if flask.request.args.get("ids"):
        lookup = {"_id": {"$in": (flask.request.args.get("ids") or "").split(",")}}

    if is_current_user_company_admin():
        # Make sure this request only searches for the current users company
        company = get_company()

        if company is None:
            flask.abort(401)

        if lookup is None:
            lookup = {}

        lookup["company"] = company["_id"]

    users = list(query_resource("users", lookup=lookup))
    return jsonify(users), 200


@blueprint.route("/users/new", methods=["POST"])
@account_manager_or_company_admin_only
def create():
    form = UserForm()
    if form.validate():
        if not _is_email_address_valid(form.email.data):
            return jsonify({"email": [gettext("Email address is already in use")]}), 400

        new_user = get_updates_from_form(form)
        add_token_data(new_user)
        user_is_company_admin = is_current_user_company_admin()
        if user_is_company_admin:
            company = get_company()
            if company is None:
                flask.abort(401)

            # Make sure this new user is associated with ``company`` and as a ``PUBLIC`` user
            new_user["company"] = company["_id"]
            new_user["user_type"] = UserRole.PUBLIC.value
        elif form.company.data:
            new_user["company"] = ObjectId(form.company.data)
        elif new_user["user_type"] != "administrator":
            return (
                jsonify({"company": [gettext("Company is required for non administrators")]}),
                400,
            )

        # Flask form won't accept default value if any form data was passed in the request.
        # So, we need to set this explicitly here.
        new_user["receive_email"] = True
        new_user["receive_app_notifications"] = True

        get_resource_service("users").post([new_user])
        send_token(new_user, token_type="new_account")
        return jsonify({"success": True}), 201
    return jsonify(form.errors), 400


def _is_email_address_valid(email):
    existing_user = get_user_by_email(email)
    return not existing_user


@blueprint.route("/users/<_id>", methods=["GET", "POST"])
@login_required
def edit(_id):
    user_is_company_admin = is_current_user_company_admin()
    user_is_admin = is_current_user_admin()
    user_is_account_mgr = is_current_user_account_mgr()
    user_is_non_admin = not (user_is_company_admin or user_is_admin or user_is_account_mgr)

    if not (user_is_admin or user_is_account_mgr or user_is_company_admin) and not is_current_user(_id):
        flask.abort(401)

    user = find_one("users", _id=ObjectId(_id))
    company = get_company()

    if user_is_company_admin and (company is None or user["company"] != ObjectId(company["_id"])):
        flask.abort(403)

    if not user:
        return NotFound(gettext("User not found"))

    if flask.request.method == "POST":
        form = UserForm(user=user)
        if form.validate_on_submit():
            if form.email.data != user["email"] and not _is_email_address_valid(form.email.data):
                return (
                    jsonify({"email": [gettext("Email address is already in use")]}),
                    400,
                )
            elif not user_is_company_admin and not form.company.data and form.user_type.data != "administrator":
                return (
                    jsonify({"company": [gettext("Company is required for non administrators")]}),
                    400,
                )

            updates = get_updates_from_form(form)
            if not user_is_admin and updates.get("user_type", "") != user.get("user_type", ""):
                flask.abort(401)

            if user_is_non_admin or user_is_company_admin:
                allowed_fields = NON_ADMIN_ALLOWED_UPDATES if user_is_non_admin else COMPANY_ADMIN_ALLOWED_UPDATES
                for field in list(updates.keys()):
                    if field not in allowed_fields:
                        updates.pop(field, None)

            get_resource_service("users").patch(ObjectId(_id), updates=updates)
            return jsonify({"success": True}), 200
        return jsonify(form.errors), 400
    return jsonify(user), 200


def get_updates_from_form(form: UserForm):
    updates = form.data
    if form.company.data:
        updates["company"] = ObjectId(form.company.data)
    if "sections" in updates:
        updates["sections"] = {section["_id"]: section["_id"] in (form.sections.data or []) for section in app.sections}

    if "products" in updates:
        product_ids = [ObjectId(productId) for productId in updates["products"]]
        products = {
            product["_id"]: product for product in query_resource("products", lookup={"_id": {"$in": product_ids}})
        }
        updates["products"] = [
            {"_id": product["_id"], "section": product["product_type"]} for product in products.values()
        ]
    return updates


@blueprint.route("/users/<_id>/validate", methods=["POST"])
@admin_only
def validate(_id):
    return _resend_token(_id, token_type="validate")


@blueprint.route("/users/<_id>/reset_password", methods=["POST"])
@account_manager_or_company_admin_only
def resend_token(_id):
    return _resend_token(_id, token_type="reset_password")


def _resend_token(user_id, token_type):
    """
    Sends a new token for a given user_id
    :param user_id: Id of the user to send the token
    :param token_type: validate or reset_password
    :return:
    """
    if not user_id:
        return BadRequest(gettext("User id not provided"))

    user = find_one("users", _id=ObjectId(user_id))

    if not user:
        return NotFound(gettext("User not found"))

    if send_token(user, token_type):
        return jsonify({"success": True}), 200

    return jsonify({"message": "Token could not be sent"}), 400


@blueprint.route("/users/<_id>", methods=["DELETE"])
@account_manager_or_company_admin_only
def delete(_id):
    """Deletes the user by given id"""
    get_resource_service("users").delete_action({"_id": ObjectId(_id)})
    return jsonify({"success": True}), 200


@blueprint.route("/users/<_id>/topics", methods=["GET"])
@login_required
def get_topics(_id):
    """Returns list of followed topics of given user"""
    if flask.session["user"] != str(_id):
        flask.abort(403)
    return jsonify({"_items": get_user_topics(_id)}), 200


@blueprint.route("/users/<_id>/topics", methods=["POST"])
@login_required
def post_topic(_id):
    """Creates a user topic"""
    user = get_user()
    if str(user["_id"]) != str(_id):
        flask.abort(403)

    topic = get_json_or_400()
    topic["user"] = user["_id"]
    topic["company"] = user.get("company")
    topic["subscribers"] = [ObjectId(uid) for uid in topic.get("subscribers") or []]

    ids = get_resource_service("topics").post([topic])
    if topic.get("is_global"):
        push_company_notification("topic_created", user_id=str(user["_id"]))
    else:
        push_user_notification("topic_created")
    return jsonify({"success": True, "_id": ids[0]}), 201


@blueprint.route("/users/<user_id>/notifications", methods=["GET"])
@login_required
def get_notifications(user_id):
    if flask.session["user"] != str(user_id):
        flask.abort(403)

    return jsonify(get_notifications_with_items()), 200


@blueprint.route("/users/<user_id>/notifications", methods=["DELETE"])
@login_required
def delete_all(user_id):
    """Deletes all notification by given user id"""
    if flask.session["user"] != str(user_id):
        flask.abort(403)

    get_resource_service("notifications").delete_action({"user": ObjectId(user_id)})
    return jsonify({"success": True}), 200


@blueprint.route("/users/<user_id>/notifications/<notification_id>", methods=["DELETE"])
@login_required
def delete_notification(user_id, notification_id):
    """Deletes the notification by given id"""
    if flask.session["user"] != str(user_id):
        flask.abort(403)

    get_resource_service("notifications").delete_action({"_id": notification_id})
    return jsonify({"success": True}), 200
