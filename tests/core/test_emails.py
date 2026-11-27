from copy import deepcopy

from quart import render_template_string, json, url_for
from jinja2 import TemplateNotFound

from newsroom.email import (
    send_item_killed_notification_email,
    send_new_item_notification_email,
    map_email_recipients_by_language,
    EmailGroup,
)
from unittest import mock
from datetime import datetime

from newsroom.types import UserResourceModel, UserRole, NotificationScheduleModel
from newsroom.email import send_user_email
from tests.fixtures import agenda_items, COMPANY_1_ID
from newsroom.tests import markers
from tests.core.utils import create_entries_for


async def test_item_notification_template(client, app, mocker):
    user = {"email": "foo@example.com", "receive_email": True, "is_enabled": True}
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

    with app.mail.record_messages() as outbox:
        async with app.app_context():
            await send_new_item_notification_email(user, "Topic", item)

        assert len(outbox) == 1
        assert outbox[0].recipients == user["email"]
        assert outbox[0].subject == "New story for followed topic: Topic"
        assert outbox[0].body == await render_template_string("""
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
        )
    assert outbox[0].html == await render_template_string("""{% extends "new_item_notification.html" %}
{% block content %}
<h1>Albion Park Greyhound VIC TAB DIVS 1-2 Monday</h1>

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
        )


EMAILS = ["default@test.com", "ca_french@test.com", "fi@test.com"]
MOCK_USERS = [
    {
        "email": EMAILS[0],
        "first_name": "Default",
        "last_name": "Test",
        "receive_email": True,
        "receive_app_notifications": True,
        "is_enabled": True,
    },
    {
        "email": EMAILS[1],
        "first_name": "CA",
        "last_name": "French",
        "locale": "fr_CA",
        "receive_email": True,
        "receive_app_notifications": True,
        "is_enabled": True,
    },
    {
        "email": EMAILS[2],
        "first_name": "Finnish",
        "last_name": "Test",
        "locale": "fi",
        "receive_email": True,
        "receive_app_notifications": True,
        "is_enabled": True,
    },
]


def mock_get_template_always_pass(_template_name_or_list):
    pass


def mock_get_template_include_fr_ca(template_name_or_list):
    if ".fr_ca." not in template_name_or_list:
        raise TemplateNotFound(template_name_or_list)


@mock.patch("flask.current_app.jinja_env.get_or_select_template", mock_get_template_always_pass)
async def test_map_email_recipients_by_language(client, app):
    await create_entries_for("users", MOCK_USERS)

    async with app.app_context():
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
async def test_map_email_recipients_by_language_fallback(client, app):
    await create_entries_for("users", MOCK_USERS)

    async with app.app_context():
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


async def test_send_user_email(app):
    user = UserResourceModel(
        first_name="foo",
        last_name="bar",
        email="foo@example.com",
        company=COMPANY_1_ID,
        notification_schedule=NotificationScheduleModel(timezone="Europe/Helsinki"),
        user_type=UserRole.PUBLIC,
        receive_email=True,
        is_enabled=True,
        is_validated=True,
    )
    date = datetime(2024, 4, 9, 11, 0, 0)
    template_kwargs = dict(date=date, topic_match_table={"wire": [], "agenda": []}, entries={})
    with app.mail.record_messages() as outbox:
        await send_user_email(user, "scheduled_notification_topic_matches_email", template_kwargs=template_kwargs)

        assert len(outbox) == 1
        assert "at 14:00 PM" in outbox[0].subject
        assert "Your Saved Topic" in outbox[0].body

    with app.mail.record_messages() as outbox:
        user.notification_schedule.timezone = "America/New_York"
        user.locale = "fr_CA"
        await send_user_email(user, "scheduled_notification_topic_matches_email", template_kwargs=template_kwargs)

        assert len(outbox) == 1
        assert "at 07:00" in outbox[0].subject
        assert "sujet" in outbox[0].body

    with app.mail.record_messages() as outbox:
        user.locale = None
        user.notification_schedule = None
        await send_user_email(user, "scheduled_notification_topic_matches_email", template_kwargs=template_kwargs)

        assert len(outbox) == 1
        assert "at 13:00 PM" in outbox[0].subject  # default timezone Europe/Prague


@markers.requires_async_celery
async def test_item_killed_notification_email(app):
    user = UserResourceModel(
        first_name="Foo",
        last_name="Bar",
        email="foo@example.com",
        user_type=UserRole.PUBLIC,
        is_enabled=True,
    )

    item = {
        "type": "text",
        "headline": "killed",
        "versioncreated": datetime.now(),
    }

    with app.mail.record_messages() as outbox:
        await send_item_killed_notification_email(user, item)
        assert len(outbox) == 1
        assert "Kill/Takedown notice" == outbox[0].subject

    item = {
        "type": "event",
    }

    with app.mail.record_messages() as outbox:
        await send_item_killed_notification_email(user, item)
        assert len(outbox) == 1
        assert "Agenda cancelled notice" == outbox[0].subject


async def test_send_user_email_on_locale_changed(app):
    event_item = deepcopy(agenda_items[0])
    event_item["coverages"] = deepcopy(agenda_items[1]["coverages"])
    event_item["planning_items"] = deepcopy(agenda_items[1]["planning_items"])

    user = UserResourceModel(
        first_name="foo",
        last_name="bar",
        email="foo@example.com",
        company=COMPANY_1_ID,
        notification_schedule=NotificationScheduleModel(timezone="Asia/Calcutta"),
        user_type=UserRole.PUBLIC,
        receive_email=True,
        is_enabled=True,
    )

    event_item["coverages"][0]["coverage_status"] = "coverage intended"

    user.locale = "fr_CA"
    with app.mail.record_messages() as outbox:
        template_kwargs = dict(item=event_item, planning_item=event_item["planning_items"][0])
        await send_user_email(user, "test_template", template_kwargs=template_kwargs)

        assert len(outbox) == 1
        print(outbox[0].body)
        assert "Event status : Planifiée" in outbox[0].body
        assert "Coverage status: Planifiée" in outbox[0].body

    user.locale = "en"
    with app.mail.record_messages() as outbox:
        template_kwargs = dict(item=event_item, planning_item=event_item["planning_items"][0])
        await send_user_email(user, "test_template", template_kwargs=template_kwargs)
        assert len(outbox) == 1
        assert "Event status : Planned" in outbox[0].body
        assert "Coverage status: Planned" in outbox[0].body
