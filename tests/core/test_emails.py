import pathlib

from flask import render_template_string, json, url_for
from jinja2 import TemplateNotFound

from newsroom.email import (
    send_new_item_notification_email,
    map_email_recipients_by_language,
    EmailGroup,
    send_email,
    handle_long_lines_html,
)
from unittest import mock


def test_item_notification_template(client, app, mocker):
    user = {"email": "foo@example.com"}
    item = {
        "_id": "tag:localhost:2018:bcc9fd45",
        "guid": "tag:localhost:2018:bcc9fd45",
        "versioncreated": json.loads('{"date": "2018-07-02T09:15:48+0000"}')["date"],
        "slugline": "Albion Park Greys",
        "headline": "Albion Park Greyhound VIC TAB DIVS 1-2 Monday",
        "service": [
            {"name": "Racing"},
        ],
        "body_html": "<p>HTML Body</p>",
        "type": "text",
    }

    item_url = url_for("wire.wire", item=item["_id"], _external=True)

    sub = mocker.patch("newsroom.email.send_email")

    with app.app_context(), app.test_request_context():
        send_new_item_notification_email(user, "Topic", item)

    sub.assert_called_with(
        to=[user["email"]],
        subject="New story for followed topic: Topic",
        text_body=render_template_string(
            """
{% extends "new_item_notification.txt" %}
{% block content %}Albion Park Greyhound VIC TAB DIVS 1-2 Monday

HTML Body

Slugline: Albion Park Greys
Headline: Albion Park Greyhound VIC TAB DIVS 1-2 Monday
Category: Racing
Published: 02/07/2018 11:15
Link: {{ item_url }}

{% endblock %}
""",
            app_name=app.config["SITE_NAME"],
            item_url=item_url,
        ),
        html_body=render_template_string(
            """
{% extends "new_item_notification.html" %}
{% block content %}<h1>Albion Park Greyhound VIC TAB DIVS 1-2 Monday</h1>

<p>HTML Body</p>

<dl>
<dt>Slugline:</dt><dd>Albion Park Greys</dd>
<dt>Headline:</dt><dd>Albion Park Greyhound VIC TAB DIVS 1-2 Monday</dd>
<dt>Category:</dt><dd>Racing</dd>
<dt>Published:</dt><dd>02/07/2018 11:15</dd>
<dt>Link:</dt><dd><a href="{{ item_url }}">{{ item_url }}</a></dd>
</dl>

{% endblock %}
""",
            app_name=app.config["SITE_NAME"],
            item_url=item_url,
        ),
    )


EMAILS = ["default@test.com", "ca_french@test.com", "fi@test.com"]
MOCK_USERS = [
    {
        "email": EMAILS[0],
        "first_name": "Default",
        "last_name": "Test",
        "receive_email": True,
        "receive_app_notifications": True,
    },
    {
        "email": EMAILS[1],
        "first_name": "CA",
        "last_name": "French",
        "locale": "fr_CA",
        "receive_email": True,
        "receive_app_notifications": True,
    },
    {
        "email": EMAILS[2],
        "first_name": "Finnish",
        "last_name": "Test",
        "locale": "fi",
        "receive_email": True,
        "receive_app_notifications": True,
    },
]


def mock_get_template_always_pass(_template_name_or_list):
    pass


def mock_get_template_include_fr_ca(template_name_or_list):
    if ".fr_ca." not in template_name_or_list:
        raise TemplateNotFound(template_name_or_list)


@mock.patch("flask.current_app.jinja_env.get_or_select_template", mock_get_template_always_pass)
def test_map_email_recipients_by_language(client, app):
    app.data.insert("users", MOCK_USERS)

    with app.test_request_context():
        email_groups = map_email_recipients_by_language(EMAILS, "test_template")

        assert "en" in email_groups
        assert email_groups["en"] == EmailGroup(
            html_template="test_template.en.html",
            text_template="test_template.en.txt",
            emails=[EMAILS[0]],
        )

        assert "fr_ca" in email_groups
        assert email_groups["fr_ca"] == EmailGroup(
            html_template="test_template.fr_ca.html",
            text_template="test_template.fr_ca.txt",
            emails=[EMAILS[1]],
        )

        assert "fi" in email_groups
        assert email_groups["fi"] == EmailGroup(
            html_template="test_template.fi.html",
            text_template="test_template.fi.txt",
            emails=[EMAILS[2]],
        )


@mock.patch(
    "flask.current_app.jinja_env.get_or_select_template",
    mock_get_template_include_fr_ca,
)
def test_map_email_recipients_by_language_fallback(client, app):
    app.data.insert("users", MOCK_USERS)

    with app.test_request_context():
        email_groups = map_email_recipients_by_language(EMAILS, "test_template")

        assert "en" in email_groups
        assert email_groups["en"] == EmailGroup(
            html_template="test_template.html",
            text_template="test_template.txt",
            emails=[EMAILS[0], EMAILS[2]],
        )

        assert "fr_ca" in email_groups
        assert email_groups["fr_ca"] == EmailGroup(
            html_template="test_template.fr_ca.html",
            text_template="test_template.fr_ca.txt",
            emails=[EMAILS[1]],
        )


def test_email_avoid_long_lines(client, app, mocker):
    sub = mocker.patch("newsroom.email._send_email.apply_async")
    with app.test_request_context():
        html = "<p>foo</p>" * 10000
        text = "a" * 500 + " " + "b" * 500 + " " + "c" * 500 + "d"
        send_email(html_body=html, text_body=text, to="to", subject="subject")
    assert len(sub.mock_calls)
    call = sub.mock_calls[0]
    check_lines_length(call.kwargs["kwargs"]["html_body"])
    check_lines_length(call.kwargs["kwargs"]["text_body"])
    lines = call.kwargs["kwargs"]["text_body"].splitlines()
    assert 3 == len(lines)
    assert 500 == len(lines[0])
    assert 500 == len(lines[1])
    assert 501 == len(lines[2])


def test_handle_long_lines_html():
    html = "<div><p>{}</p></div>".format('foo bar <a href="test">{}</a>baz'.format("loong link" * 1000) * 50)
    formatted = handle_long_lines_html(html)
    for line in formatted.splitlines():
        assert len(line) < 998, line


def test_long_lines_html_links():
    with open(pathlib.Path(__file__).parent.parent.joinpath("fixtures", "item_fixture.json")) as f:
        item = json.load(f)
    html = "<div>{}</div>".format(item["body_html"])
    formatted = handle_long_lines_html(html)
    for line in formatted.splitlines():
        assert len(line) < 998, line


def check_lines_length(text, length=998):
    lines = text.splitlines()
    for line in lines:
        assert len(line) < length
