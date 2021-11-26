import os
import arrow
from bson.objectid import ObjectId
import flask
import hashlib

from flask import current_app as app
from eve.utils import str_to_date
from flask_babel import format_time, format_date, format_datetime
from flask_babel.speaklater import LazyString
from jinja2.utils import htmlsafe_json_dumps  # type: ignore
from superdesk import get_resource_service
from superdesk.text_utils import get_text, get_word_count, get_char_count
from superdesk.utc import utcnow
from newsroom.auth import get_user
from datetime import datetime


_hash_cache = {}


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


def parse_date(datetime):
    """Return datetime instance for datetime."""
    if isinstance(datetime, str):
        try:
            return str_to_date(datetime)
        except ValueError:
            return arrow.get(datetime).datetime
    return datetime


def datetime_short(datetime):
    if datetime:
        return format_datetime(parse_date(datetime), app.config["DATETIME_FORMAT_SHORT"])


def datetime_long(datetime):
    if datetime:
        return format_datetime(parse_date(datetime), app.config["DATETIME_FORMAT_LONG"])


def date_header(datetime):
    return format_datetime(parse_date(datetime if datetime else utcnow()), app.config["DATE_FORMAT_HEADER"])


def time_short(datetime):
    if datetime:
        return format_time(parse_date(datetime), app.config["TIME_FORMAT_SHORT"])


def date_short(datetime):
    if datetime:
        return format_date(parse_date(datetime), app.config["DATE_FORMAT_SHORT"])


def plain_text(html):
    return get_text(html, content='html', lf_on_block=True) if html else ''


def word_count(html):
    return get_word_count(html or '')


def char_count(html):
    return get_char_count(html or '')


def is_admin(user=None):
    if user:
        return user.get('user_type') == 'administrator'
    return flask.session.get('user_type') == 'administrator'


def is_admin_or_internal(user=None):
    allowed_user_types = ['administrator', 'internal', 'account_management']
    if user:
        return user.get('user_type') in allowed_user_types
    return flask.session.get('user_type') in allowed_user_types


def newsroom_config():
    port = int(os.environ.get('PORT', '5000'))
    return {
        'websocket': os.environ.get('NEWSROOM_WEBSOCKET_URL', 'ws://localhost:%d' % (port + 100, )),
        'client_config': flask.current_app.config['CLIENT_CONFIG'],
    }


def hash_string(value):
    """Return SHA256 hash for given string value."""
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()


def get_date():
    return utcnow()


def sidenavs(blueprint=None):
    def blueprint_matches(nav, blueprint):
        return not nav.get('blueprint') or not blueprint or nav['blueprint'] == blueprint

    return [nav for nav in app.sidenavs if blueprint_matches(nav, blueprint)]


def section_allowed(nav, sections):
    return not nav.get('section') or sections.get(nav['section'])


def get_company_sidenavs(blueprint=None):
    user = get_user()
    company = None
    if user and user.get('company'):
        company = get_resource_service('companies').find_one(req=None, _id=user['company'])
    navs = sidenavs(blueprint)
    if company and company.get('sections'):
        return [nav for nav in navs if section_allowed(nav, company['sections'])]
    return navs


def sidenavs_by_names(names=[], blueprint=None):
    blueprint_navs = get_company_sidenavs(blueprint)
    return [nav for nav in blueprint_navs if nav.get('name') in names]


def sidenavs_by_group(group=0, blueprint=None):
    blueprint_navs = get_company_sidenavs(blueprint)
    return [nav for nav in blueprint_navs if nav.get('group') == group]


def is_admin_or_account_manager(user=None):
    allowed_user_types = ['administrator', 'account_management']
    if user:
        return user.get('user_type') in allowed_user_types
    return flask.session.get('user_type') in allowed_user_types


def authorized_settings_apps(user=None):
    if is_admin(user):
        return app.settings_apps
    if is_admin_or_account_manager(user):
        return [app for app in app.settings_apps if app.allow_account_mgr]
    return []


def get_multi_line_message(message):
    new_message = message.replace('\r', '')
    return new_message.replace('\n', '\r\n')


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
        return flask.url_for('theme', filename=filename)
    if _hash_cache.get(file) is None or app.debug:
        hash = hashlib.md5()
        with open(file, 'rb') as f:
            hash.update(f.read())
        _hash_cache[file] = hash.hexdigest()
    return flask.url_for('theme', filename=filename, h=_hash_cache.get(file, int(datetime.now().timestamp())))
