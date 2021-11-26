import bson
import flask
import pathlib
import hashlib

from datetime import datetime
from flask_babel import lazy_gettext
from newsroom.template_filters import datetime_long, parse_date


def test_parse_date():
    assert isinstance(parse_date("2017-11-03T13:49:48+0000"), datetime)
    assert isinstance(parse_date(datetime.now().isoformat()), datetime)


def test_datetime_long_str(app):
    assert isinstance(datetime_long("2017-11-03T13:49:48+0000"), str)


def test_theme_url():
    hash = hashlib.md5()
    file = pathlib.Path(__file__).parent.parent.parent.joinpath(
        "newsroom/static/theme.css"
    )
    with open(file, "rb") as f:
        hash.update(f.read())
    url = flask.render_template_string("{{ theme_url('theme.css') }}")
    assert f"?h={hash.hexdigest()}" in url


def test_to_json():
    object_id = bson.ObjectId()

    assert "foo" == flask.render_template_string("{{ foo | tojson }}", foo="foo")
    assert '{"foo":"foo"}' == str(
        flask.render_template_string("{{ obj | tojson }}", obj=dict(foo="foo"))
    )

    assert "foo" == str(
        flask.render_template_string("{{ foo | tojson }}", foo=lazy_gettext("foo"))
    )
    assert '{"foo":"foo"}' == str(
        flask.render_template_string(
            "{{ obj | tojson }}", obj=dict(foo=lazy_gettext("foo"))
        )
    )

    assert str(object_id) == str(
        flask.render_template_string("{{ _id | tojson }}", _id=object_id)
    )
    assert '{"_id":"%s"}' % (str(object_id),) == str(
        flask.render_template_string("{{ obj | tojson }}", obj=dict(_id=object_id))
    )
