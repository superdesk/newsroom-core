from functools import reduce
import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from uuid import uuid4
import regex
from typing import List, Dict, Any, Optional, Union
from pymongo.cursor import Cursor as MongoCursor

import superdesk
from superdesk.utc import utcnow
from superdesk.json_utils import try_cast
from superdesk.etree import parse_html
from superdesk.text_utils import get_text

from bson import ObjectId
from eve.utils import config, ParsedRequest
from eve_elastic.elastic import parse_date, ElasticCursor
from flask import current_app as app, json, abort, request, g, flash, session, url_for
from flask_babel import gettext

from newsroom.types import User, Company
from newsroom.template_filters import (
    time_short,
    parse_date as parse_short_date,
    format_datetime,
    is_admin,
)


DAY_IN_MINUTES = 24 * 60 - 1
MAX_TERMS_SIZE = 1000


def get_user_id():
    from newsroom.auth import get_user_id as _get_user_id

    return _get_user_id()


def query_resource(resource, lookup=None, max_results=0, projection=None, sort = None) -> Union[ElasticCursor, MongoCursor]:
    req = ParsedRequest()
    req.max_results = max_results
    req.sort = sort
    req.projection = json.dumps(projection) if projection else None
    cursor, count = app.data.find(resource, req, lookup, perform_count=False)
    return cursor


def find_one(resource, **lookup):
    req = ParsedRequest()
    return app.data.find_one(resource, req, **lookup)


def get_random_string():
    return str(uuid4())


def json_serialize_datetime_objectId(obj):
    """
    Serialize so that objectid and date are converted to appropriate format.
    """
    if isinstance(obj, datetime):
        return str(datetime.strftime(obj, config.DATE_FORMAT))

    if isinstance(obj, ObjectId):
        return str(obj)


def cast_item(o):
    if isinstance(o, (int, float, bool)):
        return o
    elif isinstance(o, str):
        return try_cast(o)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            o[i] = cast_item(v)
        return o
    elif isinstance(o, dict):
        for k, v in o.items():
            o[k] = cast_item(v)
        return o
    else:
        return o


def loads(s):
    o = json.loads(s)

    if isinstance(o, list):
        for i, v in enumerate(o):
            o[i] = cast_item(v)
        return o
    elif isinstance(o, dict):
        for k, v in o.items():
            o[k] = cast_item(v)
        return o
    else:
        return cast_item(o)


def get_entity_or_404(_id, resource):
    try:
        item = superdesk.get_resource_service(resource).find_one(req=None, _id=_id)
    except KeyError:
        item = None
    if not item:
        abort(404)
    return item


def get_entities_elastic_or_mongo_or_404(_ids, resource):
    """Finds item in elastic search as fist preference. If not configured, finds from mongo"""
    elastic = app.data._search_backend(resource)
    items = []
    if elastic:
        for id in _ids:
            item = elastic.find_one("items", req=None, _id=id)
            if not item:
                item = get_entity_or_404(id, resource)

            items.append(item)
    else:
        items = [get_entity_or_404(i, resource) for i in _ids]

    return items


def get_json_or_400():
    data = request.get_json()
    if not isinstance(data, dict):
        abort(400)
    return data


def get_type():
    item_type = request.args.get("type", "wire")
    types = {
        "wire": "items",
        "agenda": "agenda",
        "am_news": "items",
        "aapX": "items",
        "media_releases": "items",
        "monitoring": "items",
        "factcheck": "items",
    }
    return types[item_type]


def parse_date_str(date):
    if date and isinstance(date, str):
        return parse_date(date)
    return date


def parse_dates(item):
    for field in ["firstcreated", "versioncreated", "embargoed"]:
        if parse_date_str(item.get(field)):
            item[field] = parse_date_str(item[field])


def get_entity_dict(items, str_id=False):
    if str_id:
        return {str(item["_id"]): item for item in items}

    return {item["_id"]: item for item in items}


def is_json_request(request):
    """Test if request is for json content."""
    return (
        request.args.get("format") == "json"
        or request.accept_mimetypes.best_match(["application/json", "text/html"]) == "application/json"
    )


def unique_codes(key, *groups):
    """Get unique items from all lists using code."""
    codes = set()
    items = []
    for group in groups:
        for item in group:
            if item.get(key) and item[key] not in codes:
                codes.add(item[key])
                items.append(item)
    return items


def date_short(datetime):
    if datetime:
        return format_datetime(parse_short_date(datetime), "dd/MM/yyyy")


def get_agenda_dates(agenda: Dict[str, Any], date_paranthesis: bool = False) -> str:
    start = parse_date_str(agenda.get("dates", {}).get("start"))
    end = parse_date_str(agenda.get("dates", {}).get("end"))

    if start + timedelta(minutes=DAY_IN_MINUTES) < end:
        # Multi day event
        return "{} {} - {} {}".format(time_short(start), date_short(start), time_short(end), date_short(end))

    if start + timedelta(minutes=DAY_IN_MINUTES) == end:
        # All day event
        return "{} {}".format(gettext("ALL DAY"), date_short(start))

    if start == end:
        # start and end dates are the same
        return "{} {}".format(time_short(start), date_short(start))

    if date_paranthesis:
        return "{} - {} ({})".format(time_short(start), time_short(end), date_short(start))

    return "{} - {}, {}".format(time_short(start), time_short(end), date_short(start))


def get_location_string(agenda):
    location = agenda.get("location", [])

    if not location:
        return ""

    location_items = [
        location[0].get("name"),
        location[0].get("address", {}).get("line", [""])[0],
        location[0].get("address", {}).get("city") or location[0].get("address", {}).get("area"),
        location[0].get("address", {}).get("state") or location[0].get("address", {}).get("locality"),
        location[0].get("address", {}).get("postal_code"),
        location[0].get("address", {}).get("country"),
    ]

    return ", ".join([location_part for location_part in location_items if location_part])


def get_public_contacts(agenda):
    contacts = agenda.get("event", {}).get("event_contact_info", [])
    public_contacts = []
    for contact in contacts:
        if contact.get("public", False):
            public_contacts.append(
                {
                    "name": " ".join(
                        [
                            c
                            for c in [
                                contact.get("first_name"),
                                contact.get("last_name"),
                            ]
                            if c
                        ]
                    ),
                    "organisation": contact.get("organisation", ""),
                    "email": ", ".join(contact.get("contact_email", [])),
                    "phone": ", ".join([c.get("number") for c in contact.get("contact_phone", []) if c.get("public")]),
                    "mobile": ", ".join([c.get("number") for c in contact.get("mobile", []) if c.get("public")]),
                }
            )
    return public_contacts


def get_links(agenda):
    return agenda.get("event", {}).get("links", [])


def is_company_enabled(user, company=None):
    """
    Checks if the company of the user is enabled
    """
    if not user.get("company"):
        # there's no company assigned return true for admin user else false
        return True if is_admin(user) else False

    if not company:
        return False

    return company.get("is_enabled", False)


def is_company_expired(user=None, company=None):
    if app.config.get("ALLOW_EXPIRED_COMPANY_LOGINS"):
        return False
    elif user and not user.get("company"):
        return False if is_admin(user) else True
    expiry_date = (company or {}).get("expiry_date")
    if not expiry_date:
        return False
    return expiry_date.replace(tzinfo=None) <= datetime.utcnow().replace(tzinfo=None)


def is_account_enabled(user):
    """
    Checks if user account is active and approved
    """
    if not user.get("is_enabled"):
        flash(gettext("Account is disabled"), "danger")
        return False

    if not user.get("is_approved"):
        account_created = user.get("_created")

        approve_expiration = utcnow() + timedelta(days=-app.config.get("NEW_ACCOUNT_ACTIVE_DAYS", 14))
        if not account_created or account_created < approve_expiration:
            flash(gettext("Account has not been approved"), "danger")
            return False

    return True


def get_user_dict(use_globals: bool = True) -> Dict[str, User]:
    """Get all active users indexed by _id."""

    def _get_users() -> Dict[str, User]:
        all_users = superdesk.get_resource_service("users").find(where={"is_enabled": True})

        companies = get_company_dict(use_globals)

        return {
            str(user["_id"]): user
            for user in all_users
            if (
                is_company_enabled(user, companies.get(str(user.get("company"))))
                and not is_company_expired(user, companies.get(str(user.get("company"))))
            )
        }

    if not use_globals:
        return _get_users()
    elif "user_dict" not in g or app.testing:
        user_dict = _get_users()
        g.user_dict = user_dict
    return g.user_dict


def get_users_by_email(emails: List[str]):
    return query_resource("users", lookup={"email": {"$in": emails}})


def get_company_dict(use_globals: bool = True) -> Dict[str, Company]:
    """Get all active companies indexed by _id.

    Must reload when testing because there it's using single context.
    """

    def _get_companies() -> Dict[str, Company]:
        all_companies = superdesk.get_resource_service("companies").find(where={"is_enabled": True})

        return {
            str(company["_id"]): company
            for company in all_companies
            if is_company_enabled({"company": company["_id"]}, company) and not is_company_expired(company=company)
        }

    if not use_globals:
        return _get_companies()
    elif "company_dict" not in g or app.testing:
        g.company_dict = _get_companies()
    return g.company_dict


def get_cached_resource_by_id(resource, _id, black_list_keys=None):
    """If the document exist in cache then return the document form cache
    else fetch the document from the database store in the cache and return the document.


    :param str resource: Name of the resource
    :param _id: id
    :param set black_list_keys: black list of keys to exclude from the document.
    """
    item = app.cache.get(str(_id))
    if item:
        return loads(item)
    try:
        # item is not stored in cache
        item = superdesk.get_resource_service(resource).find_one(req=None, _id=_id)
    except KeyError:
        item = None
    if item:
        if not black_list_keys:
            black_list_keys = {
                "password",
                "token",
                "token_expiry",
                "_id",
                "_updated",
                "_etag",
            }
        item = {key: item[key] for key in item.keys() if key not in black_list_keys}
        app.cache.set(str(_id), json.dumps(item, default=json_serialize_datetime_objectId))
        return item
    return None


def is_valid_user(user, company) -> bool:
    """Validate if user is valid and should be able to login to the system."""
    if not user:
        flash(gettext("Invalid username or password."), "danger")
        return False

    session.pop("_flashes", None)  # remove old messages and just show one message

    if not is_admin(user) and not company:
        flash(gettext("Insufficient Permissions. Access denied."), "danger")
        return False

    if not is_account_enabled(user):
        flash(gettext("Account is disabled"), "danger")
        return False

    if not is_company_enabled(user, company):
        flash(gettext("Company account has been disabled."), "danger")
        return False

    if is_company_expired(user, company):
        flash(gettext("Company account has expired."), "danger")
        return False

    return True


def update_user_last_active(user):
    # Updated the active time for the user if required
    if not user.get("last_active") or user.get("last_active") < utcnow() + timedelta(minutes=-10):
        current_time = utcnow()
        # Set the cached version of the user
        user["last_active"] = current_time
        user["is_validated"] = True
        app.cache.set(str(user["_id"]), json.dumps(user, default=json_serialize_datetime_objectId))
        # Set the db version of the user
        superdesk.get_resource_service("users").system_update(
            ObjectId(user["_id"]), {"last_active": current_time, "is_validated": True}, user
        )


def get_items_by_id(ids, resource):
    try:
        return list(superdesk.get_resource_service(resource).find(where={"_id": {"$in": ids}}))
    except KeyError:
        return []


def get_vocabulary(id):
    vocabularies = app.data.pymongo("items").db.vocabularies
    if vocabularies is not None and vocabularies.count_documents({}) > 0 and id:
        return vocabularies.find_one({"_id": id})

    return None


def url_for_agenda(item, _external=True):
    """Get url for agenda item."""
    return url_for("agenda.index", item=item["_id"], _external=_external)


def set_original_creator(doc):
    doc["original_creator"] = get_user_id()


def set_version_creator(doc):
    doc["version_creator"] = get_user_id()


def get_items_for_user_action(_ids, item_type):
    # Getting entities from elastic first so that we get all fields
    # even those which are not a part of ItemsResource(content_api) schema.
    items = get_entities_elastic_or_mongo_or_404(_ids, item_type)

    if not items:
        return items
    elif items[0].get("type") == "text":
        for item in items:
            if item.get("slugline") and item.get("anpa_take_key"):
                item["slugline"] = "{0} | {1}".format(item["slugline"], item["anpa_take_key"])
    elif items[0].get("type") == "agenda":
        # Import here to prevent circular imports
        from newsroom.auth import get_company
        from newsroom.companies.utils import restrict_coverage_info
        from newsroom.agenda.utils import remove_restricted_coverage_info

        if restrict_coverage_info(get_company()):
            remove_restricted_coverage_info(items)

    return items


def get_utcnow():
    """added for unit tests"""
    return datetime.utcnow()


def today(time, offset):
    user_local_date = get_utcnow() - timedelta(minutes=offset)
    local_start_date = datetime.strptime("%sT%s" % (user_local_date.strftime("%Y-%m-%d"), time), "%Y-%m-%dT%H:%M:%S")
    return local_start_date


def format_date(date, time, offset):
    if date == "now/d":
        return today(time, offset)
    if date == "now/w":
        _today = today(time, offset)
        monday = _today - timedelta(days=_today.weekday())
        return monday
    if date == "now/M":
        month = today(time, offset).replace(day=1)
        return month
    return datetime.strptime("%sT%s" % (date, time), "%Y-%m-%dT%H:%M:%S")


def get_local_date(date, time, offset):
    local_dt = format_date(date, time, offset)
    return pytz.utc.normalize(local_dt.replace(tzinfo=pytz.utc) + timedelta(minutes=offset))


def get_end_date(date_range, start_date):
    if date_range == "now/d":
        return start_date
    if date_range == "now/w":
        return start_date + timedelta(days=6)
    if date_range == "now/M":
        return start_date + relativedelta(months=+1) - timedelta(days=1)
    return start_date


def deep_get(val: Dict[str, Any], keys: str, default: Optional[Any] = None) -> Any:
    """Helper function to get nested value from a dictionary using dot notation

    i.e.
    account = {"details": {"name": {"first": "John"}}}
    deep_get(account, "details.name.first")  # "John"
    deep_get(account, "details.name.last")  # None
    deep_get(account, "details.name.last", "Not Defined")  # "Not Defined"
    """

    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default or {},
        keys.split("."),
        val,
    )


def split_words(text: str) -> List[str]:
    """Get word count for given plain text.

    Any changes to this code **must** be reflected in the typescript version as well
    Copied from ``superdesk-core:superdesk/text_utils.py:get_text_word_count``
    """

    flags = regex.MULTILINE | regex.UNICODE
    initial_text_trimmed = text.strip()

    if len(initial_text_trimmed) < 1:
        return []

    r0 = get_text(initial_text_trimmed, space_on_elements=True)
    r1 = regex.sub(r"\n", " ", r0, flags=flags)

    # Remove spaces between two numbers
    # 1 000 000 000 -> 1000000000
    r2 = regex.sub(r"([0-9]) ([0-9])", "\\1\\2", r1, flags=flags)

    # remove anything that is not a unicode letter, a space, comma or a number
    r3 = regex.sub(r"[^\p{L} 0-9,]", "", r2, flags=flags)

    # replace two or more spaces with one space
    r4 = regex.sub(r" {2,}", " ", r3, flags=flags)

    return r4.strip().split(" ")


def short_highlighted_text(html: str, max_length: int = 40, output_html: bool = True) -> str:
    """Returns first paragraph with highlighted text, and truncates output to ``max_length`` words

    Any changes to this code **must** be reflected in the typescript version as well
    Copied from ``assets/wire/utils.ts:shortHighlightedtext``
    """

    doc = parse_html(html, content="html")
    try:
        parent_element = doc.xpath('//span[@class="es-highlight"]/..')[0]
    except IndexError:
        words = split_words(html)

        if len(words) >= max_length:
            return " ".join(words[:max_length]) + "..."
        else:
            return html

    text = ""
    count = 0
    for content in parent_element.itertext():
        if count >= max_length:
            break

        content = content.strip()
        words = split_words(content)
        word_count = len(words)
        remaining_count = max_length - count

        if word_count <= remaining_count:
            text += content + " "
            count += word_count
        else:
            text += " ".join(words[:remaining_count])
            count += remaining_count

    truncated_text = text.strip()
    highlighted_spans = parent_element.xpath('//span[@class="es-highlight"]')
    output = truncated_text
    highlighted_text = ""
    last_index = 0

    for span in highlighted_spans:
        span_text = span.text.strip()

        try:
            span_index = truncated_text.index(span_text, last_index)
            span_start = span_index
            span_end = span_start + len(span_text)

            highlighted_text += output[last_index:span_start]

            if output_html:
                highlighted_text += f'<span class="es-highlight">{span_text}</span>'
            else:
                highlighted_text += f"*{span_text}*"

            last_index = span_end
        except ValueError:
            # ``span_text`` not found
            pass

    output = highlighted_text + output[last_index:]

    return output + ("" if count > max_length else "...")
