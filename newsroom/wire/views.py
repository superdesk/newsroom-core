import io
from typing import Dict
import flask
import zipfile
import superdesk

from operator import itemgetter
from flask import current_app as app, request, jsonify
from eve.render import send_response
from eve.methods.get import get_internal
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from flask_babel import gettext
from superdesk.utc import utcnow
from superdesk import get_resource_service
from superdesk.default_settings import strtobool
from newsroom.auth.utils import check_user_has_products, is_valid_session

from newsroom.navigations.navigations import get_navigations_by_company
from newsroom.products.products import get_products_by_company
from newsroom.wire import blueprint
from newsroom.wire.utils import update_action_list
from newsroom.auth import get_company, get_user, get_user_id, get_user_required
from newsroom.decorator import login_required, admin_only, section, clear_session_and_redirect_to_login
from newsroom.topics import get_user_topics, get_user_folders, get_company_folders
from newsroom.email import send_template_email, get_language_template_name
from newsroom.utils import (
    get_entity_or_404,
    get_json_or_400,
    parse_dates,
    get_type,
    is_json_request,
    query_resource,
    get_agenda_dates,
    get_location_string,
    get_public_contacts,
    get_links,
    get_items_for_user_action,
)
from newsroom.notifications import (
    push_user_notification,
    push_notification,
    save_user_notifications,
    UserNotification,
)
from newsroom.template_filters import is_admin_or_internal
from newsroom.gettext import get_session_locale
from newsroom.public.views import (
    render_public_dashboard,
    PUBLIC_DASHBOARD_CONFIG_CACHE_KEY,
    PUBLIC_DASHBOARD_CARDS_CACHE_KEY,
    PUBLIC_DASHBOARD_ITEMS_CACHE_KEY,
)

from .search import get_bookmarks_count
from .items import get_items_for_dashboard
from ..upload import ASSETS_RESOURCE, get_upload

HOME_ITEMS_CACHE_KEY = "home_items"
HOME_EXTERNAL_ITEMS_CACHE_KEY = "home_external_items"


def get_services(user):
    services = app.config["SERVICES"]
    for service in services:
        service.setdefault("is_active", True)
    company = get_company(user)
    if company and company.get("services"):
        for service in services:
            service["is_active"] = bool(company["services"].get(service["code"]))
    return services


def set_permissions(item, section="wire", ignore_latest=False):
    permitted = superdesk.get_resource_service("{}_search".format(section)).has_permissions(item, ignore_latest)
    set_item_permission(item, permitted)


def set_item_permission(item, permitted=True):
    if not item:
        return

    item["_access"] = permitted
    if not item["_access"]:
        item.pop("body_text", None)
        item.pop("body_html", None)
        item.pop("renditions", None)
        item.pop("associations", None)


def get_view_data() -> Dict:
    user = get_user_required()
    company = get_company(user)
    topics = get_user_topics(user["_id"]) if user else []
    company_id = str(user["company"]) if user and user.get("company") else None
    user_folders = get_user_folders(user, "wire") if user else []
    company_folders = get_company_folders(company, "wire") if company else []
    products = get_products_by_company(company, product_type="wire") if company else []

    check_user_has_products(user, products)

    return {
        "user": user,
        "company": company_id,
        "topics": [t for t in topics if t.get("topic_type") == "wire"],
        "formats": [
            {"format": f["format"], "name": f["name"], "assets": f["assets"]}
            for f in app.download_formatters.values()
            if "wire" in f["types"]
        ],
        "navigations": get_navigations_by_company(company, product_type="wire") if company else [],
        "products": products,
        "saved_items": get_bookmarks_count(user["_id"], "wire"),
        "context": "wire",
        "ui_config": get_resource_service("ui_config").get_section_config("wire"),
        "groups": app.config.get("WIRE_GROUPS", []),
        "user_folders": user_folders,
        "company_folders": company_folders,
    }


def get_items_by_card(cards, company_id):
    cache_key = "{}{}".format(HOME_ITEMS_CACHE_KEY, company_id or "")
    if app.cache.get(cache_key):
        return app.cache.get(cache_key)

    items_by_card = get_items_for_dashboard(cards)
    app.cache.set(cache_key, items_by_card, timeout=app.config.get("DASHBOARD_CACHE_TIMEOUT", 300))
    return items_by_card


def delete_dashboard_caches():
    app.cache.delete(HOME_ITEMS_CACHE_KEY)
    app.cache.delete(PUBLIC_DASHBOARD_CONFIG_CACHE_KEY)
    app.cache.delete(PUBLIC_DASHBOARD_CARDS_CACHE_KEY)
    app.cache.delete(PUBLIC_DASHBOARD_ITEMS_CACHE_KEY)
    for company in query_resource("companies"):
        app.cache.delete(f"{HOME_ITEMS_CACHE_KEY}{company['_id']}")


def get_personal_dashboards_data(user, company, topics):
    def get_topic_items(topic):
        query = superdesk.get_resource_service("wire_search").get_topic_query(topic, user, company)
        return list(superdesk.get_resource_service("wire_search").get_items_by_query(query, size=4))

    def _get_topic_data(topic_id):
        for topic in topics:
            if topic["_id"] == topic_id:
                items = get_topic_items(topic)
                if items:
                    return {
                        "_id": topic["_id"],
                        "items": items,
                    }
                break
        return None

    def _get_dashboard_data(dashboard, index):
        return {
            "dashboard_id": f"d{index}",
            "dashboard_name": dashboard.get("name", ""),
            "topic_items": list(
                filter(None, [_get_topic_data(topic_id) for topic_id in dashboard.get("topic_ids") or []])
            ),
        }

    dashboards = user.get("dashboards") or []
    return [_get_dashboard_data(dashboard, i) for i, dashboard in enumerate(dashboards)]


def get_home_data():
    user = get_user()
    company = get_company(user)
    cards = list(query_resource("cards", lookup={"dashboard": "newsroom"}))
    company_id = str(user["company"]) if user and user.get("company") else None
    topics = get_user_topics(user["_id"]) if user else []

    return {
        "cards": cards,
        "products": get_products_by_company(company) if company else [],
        "user": str(user["_id"]) if user else None,
        "userProducts": user.get("products") or [],
        "userType": user.get("user_type"),
        "company": company_id,
        "formats": [
            {
                "format": f["format"],
                "name": f["name"],
                "types": f["types"],
                "assets": f["assets"],
            }
            for f in app.download_formatters.values()
        ],
        "context": "wire",
        "topics": topics,
        "ui_config": get_resource_service("ui_config").get_section_config("home"),
        "groups": app.config.get("WIRE_GROUPS", []),
        "personalizedDashboards": get_personal_dashboards_data(user, company, topics),
    }


def get_previous_versions(item):
    if item.get("ancestors"):
        ancestors = superdesk.get_resource_service("wire_search").get_items(item["ancestors"])
        return sorted(ancestors, key=itemgetter("versioncreated"), reverse=True)
    return []


@blueprint.route("/")
def index():
    if not is_valid_session():
        return (
            render_public_dashboard() if app.config.get("PUBLIC_DASHBOARD") else clear_session_and_redirect_to_login()
        )

    return flask.render_template("home.html", data=get_home_data())


@blueprint.route("/media_card_external/<card_id>")
@login_required
def get_media_card_external(card_id):
    cache_id = "{}_{}".format(HOME_EXTERNAL_ITEMS_CACHE_KEY, card_id)

    if app.cache.get(cache_id):
        card_items = app.cache.get(cache_id)
    else:
        card = get_entity_or_404(card_id, "cards")
        card_items = app.get_media_cards_external(card)
        app.cache.set(cache_id, card_items, timeout=app.config.get("DASHBOARD_CACHE_TIMEOUT", 300))

    return flask.jsonify({"_items": card_items})


@blueprint.route("/card_items")
@login_required
def get_card_items():
    user = get_user()
    cards = list(query_resource("cards", lookup={"dashboard": "newsroom"}))
    company_id = str(user["company"]) if user and user.get("company") else None
    items_by_card = get_items_by_card(cards, company_id)
    return flask.jsonify({"_items": items_by_card})


@blueprint.route("/wire")
@login_required
@section("wire")
def wire():
    return flask.render_template("wire_index.html", data=get_view_data())


@blueprint.route("/bookmarks_wire")
@login_required
def bookmarks():
    data = get_view_data()
    data["bookmarks"] = True
    return flask.render_template("wire_bookmarks.html", data=data)


@blueprint.route("/wire/search")
@login_required
@section("wire")
def search():
    if "prepend_embargoed" in request.args or app.config["PREPEND_EMBARGOED_TO_WIRE_SEARCH"]:
        args = request.args.to_dict()
        args["prepend_embargoed"] = strtobool(
            str(request.args.get("prepend_embargoed", app.config["PREPEND_EMBARGOED_TO_WIRE_SEARCH"]))
        )
        request.args = ImmutableMultiDict(args)
    response = get_internal("wire_search")
    return send_response("wire_search", response)


@blueprint.route("/download", methods=["POST"])
@login_required
def download():
    user = get_user(required=True)
    data = flask.request.json
    _format = data.get("format", "text")
    item_type = get_type(data.get("type"))
    items = get_items_for_user_action(data["items"], item_type)
    _file = io.BytesIO()
    formatter = app.download_formatters[_format]["formatter"]
    mimetype = None
    attachment_filename = "%s-newsroom.zip" % utcnow().strftime("%Y%m%d%H%M")
    if formatter.get_mediatype() == "picture":
        if len(items) == 1:
            try:
                picture = formatter.format_item(items[0], item_type=item_type)
                return get_upload(picture["media"], filename="baseimage%s" % picture["file_extension"])
            except ValueError:
                return flask.abort(404)
        else:
            with zipfile.ZipFile(_file, mode="w") as zf:
                for item in items:
                    try:
                        picture = formatter.format_item(item, item_type=item_type)
                        file = flask.current_app.media.get(picture["media"], ASSETS_RESOURCE)
                        zf.writestr("baseimage%s" % picture["file_extension"], file.read())
                    except ValueError:
                        pass
            _file.seek(0)
    elif len(items) == 1 or _format == "monitoring":
        item = items[0]
        args_item = item if _format != "monitoring" else items
        parse_dates(item)  # fix for old items
        _file.write(formatter.format_item(args_item, item_type=item_type))
        _file.seek(0)
        mimetype = formatter.get_mimetype(item)
        attachment_filename = secure_filename(formatter.format_filename(item))
    elif formatter.MULTI and len(items) != 1:
        # if we have multiple items, so in this case we stored their data in one csv file.
        csv_data, attachment_filename = formatter.format_events(items, item_type=item_type)
        _file.write(csv_data)
        _file.seek(0)
    else:
        with zipfile.ZipFile(_file, mode="w") as zf:
            for item in items:
                parse_dates(item)  # fix for old items
                zf.writestr(
                    secure_filename(formatter.format_filename(item)),
                    formatter.format_item(item, item_type=item_type),
                )
        _file.seek(0)

    update_action_list(data["items"], "downloads", force_insert=True)
    get_resource_service("history").create_history_record(items, "download", user, request.args.get("type", "wire"))
    return flask.send_file(
        _file,
        mimetype=mimetype,
        attachment_filename=attachment_filename,
        as_attachment=True,
    )


@blueprint.route("/wire_share", methods=["POST"])
@login_required
def share():
    current_user = get_user(required=True)
    item_type = get_type()
    data = get_json_or_400()
    assert data.get("users")
    assert data.get("items")
    items = get_items_for_user_action(data.get("items"), item_type)
    for user_id in data["users"]:
        user = superdesk.get_resource_service("users").find_one(req=None, _id=user_id)

        if not user or not user.get("email"):
            continue
        template_kwargs = {
            "app_name": app.config["SITE_NAME"],
            "recipient": user,
            "sender": current_user,
            "items": items,
            "message": data.get("message"),
            "section": request.args.get("type", "wire"),
            "subject_name": items[0].get("headline") or items[0].get("name"),
        }
        if item_type == "agenda":
            template_kwargs["maps"] = data.get("maps") if app.config.get("GOOGLE_MAPS_KEY") else []
            template_kwargs["dateStrings"] = [get_agenda_dates(item) for item in items]
            template_kwargs["locations"] = [get_location_string(item) for item in items]
            template_kwargs["contactList"] = [get_public_contacts(item) for item in items]
            template_kwargs["linkList"] = [get_links(item) for item in items]
            template_kwargs["is_admin"] = is_admin_or_internal(user)

        save_user_notifications(
            [
                UserNotification(
                    resource=item_type,
                    action="share",
                    user=user["_id"],
                    item=items[0]["_id"],
                    data=dict(
                        shared_by=dict(
                            _id=current_user["_id"],
                            first_name=current_user["first_name"],
                            last_name=current_user["last_name"],
                        ),
                        items=[i["_id"] for i in items],
                    ),
                )
            ]
        )

        send_template_email(
            to=[user["email"]],
            template=f"share_{item_type}",
            template_kwargs=template_kwargs,
        )
    update_action_list(data.get("items"), "shares", item_type=item_type)
    get_resource_service("history").create_history_record(
        items, "share", current_user, request.args.get("type", "wire")
    )
    return flask.jsonify(), 201


@blueprint.route("/wire", methods=["DELETE"])
@admin_only
def remove_wire_items():
    data = get_json_or_400()
    assert data.get("items")

    items_service = get_resource_service("items")
    versions_service = get_resource_service("items_versions")

    ids = []
    for doc in items_service.get_from_mongo(req=None, lookup={"_id": {"$in": data["items"]}}):
        ids.append(doc["_id"])
        ids.extend(doc.get("ancestors") or [])

    if not ids:
        flask.abort(404, gettext("Not found"))

    docs = list(doc for doc in items_service.get_from_mongo(req=None, lookup={"_id": {"$in": ids}}))

    for doc in docs:
        items_service.on_delete(doc)

    items_service.delete({"_id": {"$in": ids}})

    for doc in docs:
        items_service.on_deleted(doc)
        versions_service.on_item_deleted(doc)

    push_notification("items_deleted", ids=ids)

    return flask.jsonify(), 200


@blueprint.route("/wire_bookmark", methods=["POST", "DELETE"])
@login_required
def bookmark():
    """Bookmark an item.

    Stores user id into item.bookmarks array.
    Uses mongodb to update the array and then pushes updated array to elastic.
    """
    data = get_json_or_400()
    assert data.get("items")
    update_action_list(data.get("items"), "bookmarks", item_type="items")
    user_id = get_user_id()
    push_user_notification("saved_items", count=get_bookmarks_count(user_id, "wire"))
    return flask.jsonify(), 200


@blueprint.route("/wire/<_id>/copy", methods=["POST"])
@login_required
def copy(_id):
    item_type = get_type()
    item = get_entity_or_404(_id, item_type)

    template_filename = "copy_agenda_item" if item_type == "agenda" else "copy_wire_item"
    locale = (get_session_locale() or "en").lower()
    template_name = get_language_template_name(template_filename, locale, "txt")

    template_kwargs = {"item": item}
    if item_type == "agenda":
        template_kwargs.update(
            {
                "location": "" if item_type != "agenda" else get_location_string(item),
                "contacts": get_public_contacts(item),
                "calendars": ", ".join([calendar.get("name") for calendar in item.get("calendars") or []]),
            }
        )
    copy_data = flask.render_template(template_name, **template_kwargs).strip()

    update_action_list([_id], "copies", item_type=item_type)
    get_resource_service("history").create_history_record([item], "copy", get_user(), request.args.get("type", "wire"))
    return flask.jsonify({"data": copy_data}), 200


@blueprint.route("/wire/<_id>/versions")
@login_required
def versions(_id):
    item = get_entity_or_404(_id, "items")
    items = get_previous_versions(item)
    return flask.jsonify({"_items": items})


@blueprint.route("/wire/<_id>")
@login_required
def item(_id):
    items = get_items_for_user_action([_id], "items")
    if not items:
        return

    item = items[0]
    set_permissions(
        item,
        "wire",
        False if flask.request.args.get("ignoreLatest") == "false" else True,
    )
    display_char_count = get_resource_service("ui_config").get_section_config("wire").get("char_count", False)
    if is_json_request(flask.request):
        return flask.jsonify(item)
    if not item.get("_access"):
        return flask.render_template("wire_item_access_restricted.html", item=item)
    previous_versions = get_previous_versions(item)
    template = "wire_item.html"
    data = {"item": item}
    if "print" in flask.request.args:
        if flask.request.args.get("monitoring_profile"):
            data.update(flask.request.view_args)
            template = "monitoring_export.html"
        else:
            template = "wire_item_print.html"

        update_action_list([_id], "prints", force_insert=True)
        get_resource_service("history").create_history_record(
            [item], "print", get_user(), request.args.get("type", "wire")
        )

    return flask.render_template(
        template,
        **data,
        previous_versions=previous_versions,
        display_char_count=display_char_count,
    )


@blueprint.route("/wire/items/<_ids>")
@login_required
def items(_ids):
    item_ids = _ids.split(",")
    items = superdesk.get_resource_service("wire_search").get_items(item_ids)
    for item in items:
        set_permissions(
            item,
            "wire",
            False if flask.request.args.get("ignoreLatest") == "false" else True,
        )

    return jsonify(items.docs), 200
