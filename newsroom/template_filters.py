import os
from typing import Optional, List, Dict, Any, Union
import arrow
from bson.objectid import ObjectId
import flask
import hashlib
import logging

from flask import current_app as app
from eve.utils import str_to_date
from flask_babel import format_time, format_date, format_datetime, get_locale, lazy_gettext
from flask_babel.speaklater import LazyString
from jinja2.utils import htmlsafe_json_dumps  # type: ignore
from superdesk.text_utils import get_text, get_word_count, get_char_count
from superdesk.utc import utcnow
from datetime import datetime
from newsroom.auth import get_company
from newsroom.gettext import set_session_timezone, get_session_timezone, clear_session_timezone
from enum import Enum

from newsroom.types import User
from newsroom.user_roles import UserRole


logger = logging.getLogger(__name__)
_hash_cache = {}


class ScheduleType(Enum):
    ALL_DAY = "ALL_DAY"
    MULTI_DAY = "MULTI_DAY"
    NO_DURATION = "NO_DURATION"
    REGULAR = "REGULAR"


def get_client_format(key) -> Optional[str]:
    locale = str(get_locale())
    try:
        return app.config["CLIENT_LOCALE_FORMATS"][locale][key]
    except KeyError:
        pass
    try:
        return app.config["CLIENT_LOCALE_FORMATS"][app.config["DEFAULT_LANGUAGE"]][key]
    except KeyError:
        pass
    return None


def to_json(value):
    """Jinja filter to address the encoding of special values to json.

    Make it consistent to return strings without surrounding ""
    so for string values it should be used with '' in the template::

        const user_id = '{{ user["_id"] | tojson }}';

    """
    if isinstance(value, LazyString):
        value = str(value)
    if isinstance(value, ObjectId):
        value = str(value)
    return htmlsafe_json_dumps(obj=value, dumper=app.json_encoder().dumps)


def parse_date(datetime: Union[str, datetime]) -> datetime:
    """Return datetime instance for datetime."""
    if isinstance(datetime, str):
        try:
            parsed = str_to_date(datetime)
            if not parsed:
                raise ValueError()
            return parsed
        except ValueError:
            return arrow.get(datetime).datetime
    return datetime


def get_schedule_type(start: datetime, end: Optional[datetime], all_day: bool, no_end_time: bool) -> ScheduleType:
    """
    Determine the schedule type based on event start and end times.

    params :
    - start (datetime): Start time of the event.
    - end (datetime): End time of the event.
    - all_day (bool): True if the event is an all-day event.
    - no_end_time (bool): True if the event has no specified end time.

    return:
    ScheduleType: The type of schedule (ALL_DAY, NO_DURATION, MULTI_DAY, REGULAR).
    """
    duration = int((end - start).total_seconds() / 60) if not no_end_time and end else 0
    DAY_IN_MINUTES = 24 * 60 - 1

    if all_day:
        return ScheduleType.ALL_DAY if duration in (0, DAY_IN_MINUTES) else ScheduleType.MULTI_DAY

    if no_end_time:
        return ScheduleType.NO_DURATION

    if duration >= DAY_IN_MINUTES and start.date() != (end.date() if end else None):
        return ScheduleType.MULTI_DAY

    if duration <= DAY_IN_MINUTES and start.date() == (end.date() if end else None):
        return ScheduleType.ALL_DAY

    if duration == 0 and start.time() == (end.time() if end else None):
        return ScheduleType.NO_DURATION

    return ScheduleType.REGULAR


def is_item_tbc(item: dict) -> bool:
    event_tbc = item.get("event", {}).get("_time_to_be_confirmed", False)
    planning = item.get("planning_items", [])
    return event_tbc or (planning and planning[0].get("_time_to_be_confirmed", False))


def format_event_datetime(item: dict) -> str:
    date_info = item.get("dates", {})

    if not date_info:
        return ""

    tz = date_info.get("tz", get_session_timezone())
    try:
        # Set the session timezone
        set_session_timezone(tz)

        start = parse_date(date_info.get("start"))
        end = parse_date(date_info.get("end")) if date_info.get("end") else None
        all_day = date_info.get("all_day")
        no_end_time = date_info.get("no_end_time")
        is_tbc_item = is_item_tbc(item)

        schedule_type = get_schedule_type(start, end, all_day, no_end_time)

        formatted_start = datetime_long(start)
        formatted_end = datetime_long(end) if end else None

        if is_tbc_item:
            if schedule_type == ScheduleType.MULTI_DAY:
                return lazy_gettext("Date: {start} to {end} ({tz}) (Time to be confirmed)").format(
                    start=formatted_start, end=formatted_end, tz=tz
                )

            else:
                return lazy_gettext("Date: {start} ({tz}) (Time to be confirmed)").format(start=formatted_start, tz=tz)

        elif schedule_type in (ScheduleType.ALL_DAY, ScheduleType.NO_DURATION):
            return lazy_gettext("Date: {start} ({tz})").format(start=formatted_start, tz=tz)

        elif schedule_type == ScheduleType.MULTI_DAY:
            return lazy_gettext("Date: {start} to {end} ({tz})").format(start=formatted_start, end=formatted_end, tz=tz)
        elif schedule_type == ScheduleType.REGULAR:
            return lazy_gettext("Time: {start_time} to {end_time} on Date: {date} ({tz})").format(
                start_time=notification_time(start),
                end_time=notification_time(end),
                date=notification_date(start),
                tz=tz,
            )
        else:
            # Default
            return lazy_gettext("Date: {start_time} {start_date} to {end_time} {end_date} ({tz})").format(
                start_time=notification_time(start),
                start_date=notification_date(start),
                end_time=notification_time(end),
                end_date=notification_date(end),
                tz=tz,
            )

    finally:
        # clear session timezone
        clear_session_timezone()


def datetime_short(datetime):
    if datetime:
        return format_datetime(parse_date(datetime), app.config["DATETIME_FORMAT_SHORT"])


def datetime_long(datetime):
    if datetime:
        return format_datetime(parse_date(datetime), app.config["DATETIME_FORMAT_LONG"])


def date_header(datetime):
    _format = get_client_format("DATE_FORMAT_HEADER")
    return format_datetime(parse_date(datetime if datetime else utcnow()), _format)


def time_short(datetime):
    if datetime:
        return format_time(parse_date(datetime), app.config["TIME_FORMAT_SHORT"])


def date_short(datetime):
    if datetime:
        return format_date(parse_date(datetime), app.config["DATE_FORMAT_SHORT"])


def notification_time(datetime):
    if datetime:
        return format_time(parse_date(datetime), get_client_format("NOTIFICATION_EMAIL_TIME_FORMAT"))


def notification_date(datetime):
    if datetime:
        return format_date(parse_date(datetime), get_client_format("NOTIFICATION_EMAIL_DATE_FORMAT"))


def notification_datetime(datetime):
    if datetime:
        return format_datetime(parse_date(datetime), get_client_format("NOTIFICATION_EMAIL_DATETIME_FORMAT"))


def plain_text(html) -> str:
    if not html:
        return ""

    # Remove newlines, and strip whitespace, before converting tag blocks to newlines
    text = "".join([line.strip() for line in html.split("\n")])

    # Remove the final newline, as newlines are added after each block, and we don't need the last one
    return (get_text(text, content="html", lf_on_block=True) if text else "")[:-1]


def word_count(html):
    return get_word_count(html or "")


def char_count(html):
    return get_char_count(html or "")


def is_admin(user=None):
    if user:
        return user.get("user_type") == "administrator"
    return flask.session.get("user_type") == "administrator"


def is_admin_or_internal(user=None):
    allowed_user_types = ["administrator", "internal", "account_management"]
    if user:
        return user.get("user_type") in allowed_user_types
    return flask.session.get("user_type") in allowed_user_types


def newsroom_config():
    port = int(os.environ.get("PORT", "5000"))
    return {
        "websocket": os.environ.get("NEWSROOM_WEBSOCKET_URL", "ws://localhost:%d" % (port + 100,)),
        "client_config": flask.current_app.config["CLIENT_CONFIG"],
    }


def hash_string(value):
    """Return SHA256 hash for given string value."""
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def get_date():
    return utcnow()


def sidenavs(blueprint=None):
    def blueprint_matches(nav, blueprint):
        return not nav.get("blueprint") or not blueprint or nav["blueprint"] == blueprint

    locale = str(get_locale())

    return [
        nav
        for nav in app.sidenavs
        if blueprint_matches(nav, blueprint) and (nav.get("locale") is None or nav["locale"] == locale)
    ]


def section_allowed(nav, sections):
    return not nav.get("section") or sections.get(nav["section"])


def get_company_sidenavs(blueprint=None):
    from newsroom.auth.utils import get_user_sections, get_user

    user = get_user()
    sections = get_user_sections(user)
    navs = sidenavs(blueprint)
    if sections:
        return [nav for nav in navs if section_allowed(nav, sections)]
    return navs


def sidenavs_by_names(names=[], blueprint=None):
    blueprint_navs = get_company_sidenavs(blueprint)
    return [nav for nav in blueprint_navs if nav.get("name") in names]


def sidenavs_by_group(group=0, blueprint=None):
    blueprint_navs = get_company_sidenavs(blueprint)
    return [nav for nav in blueprint_navs if nav.get("group") == group]


def is_user_type_allowed(allowed_user_types, user=None):
    if user:
        return user.get("user_type") in allowed_user_types
    return flask.session.get("user_type") in allowed_user_types


def is_admin_or_account_manager(user=None):
    return is_user_type_allowed(["administrator", "account_management"], user)


def is_admin_manager_or_company_admin(user=None):
    return is_user_type_allowed(["administrator", "account_management", "company_admin"], user)


def is_company_admin(user=None):
    return (user.get("user_type") if user else flask.session.get("user_type")) == UserRole.COMPANY_ADMIN.value


def authorized_settings_apps(user=None):
    if is_admin(user):
        return app.settings_apps
    if is_admin_or_account_manager(user):
        return [app for app in app.settings_apps if app.allow_account_mgr]
    return []


def get_multi_line_message(message):
    new_message = message.replace("\r", "")
    return new_message.replace("\n", "\r\n")


def get_theme_file(filename):
    for folder in app._theme_folders:
        file = os.path.realpath(os.path.join(folder, filename))
        if os.path.exists(file):
            return file


def theme_url(filename):
    """Get url for theme file.

    There will be a hash of the file added to it
    in order to force refresh on changes.
    """
    file = get_theme_file(filename)
    assert file
    if not file:  # this should not really happen
        return flask.url_for("theme", filename=filename)
    if _hash_cache.get(file) is None or app.debug:
        hash = hashlib.md5()
        with open(file, "rb") as f:
            hash.update(f.read())
        _hash_cache[file] = hash.hexdigest()
    return flask.url_for(
        "theme",
        filename=filename,
        h=_hash_cache.get(file, int(datetime.now().timestamp())),
    )


def get_slugline(item, with_take_key: bool = False):
    if not item or not item.get("slugline"):
        return ""

    slugline = item["slugline"].strip()
    take_key = item.get("anpa_take_key") or ""
    take_key_suffix = f" | {take_key}"
    if with_take_key and item.get("anpa_take_key") and not slugline.endswith(take_key_suffix):
        slugline += take_key_suffix

    return slugline


def initials(name):
    return "".join([piece[0].upper() for piece in name.split(" ") if piece])


def get_highlighted_field(item: Dict[str, Any], fields: List[str]) -> str:
    for field in fields:
        if not item.get(field):
            continue

        try:
            return item["es_highlight"][field][0]
        except (IndexError, KeyError):
            return item[field]

    logger.warning(f"Failed to find any highlighted fields {fields}")
    return ""


def get_item_category_names(item: Dict[str, Any]) -> str:
    if not len(item.get("service") or []):
        return ""

    return ", ".join([category["name"] for category in item["service"]])


def get_ga_user_properties(user: User) -> Dict[str, str]:
    if not user:
        return {}
    company = get_company(user)
    return {
        "company": (company.get("name") if company else "") or "none",
        "user": f"{user['first_name']} {user['last_name'][:1]}".strip(),
        "user_internal_id": str(user.get("_id") or ""),  # user_id is reserved name
    }
