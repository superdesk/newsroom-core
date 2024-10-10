import base64
import email.policy as email_policy

from lxml import etree
from typing_extensions import TypedDict
from typing import List, Optional, Dict, Any, Union

from quart_babel import gettext
from flask_mail import Attachment, Message
from jinja2 import TemplateNotFound

from superdesk.logging import logger
from superdesk import get_resource_service
from superdesk.core import get_app_config, get_current_app
from superdesk.core.resources import ResourceModel
from superdesk.flask import render_template, url_for

from newsroom.gettext import get_user_timezone
from newsroom.types import Company, User, Country, CompanyType, UserResourceModel
from newsroom.celery_app import celery
from newsroom.template_loaders import template_locale
from newsroom.utils import (
    get_agenda_dates,
    get_location_string,
    get_links,
    get_public_contacts,
    url_for_agenda,
)
from newsroom.template_filters import is_admin_or_internal


class NewsroomMessage(Message):
    def _message(self):
        msg = super()._message()
        msg.policy = email_policy.SMTP
        return msg


class EmailGroup(TypedDict):
    html_template: str
    text_template: str
    emails: List[str]


MAX_LINE_LENGTH = 998 - 50  # RFC 5322 - buffer for html indentation


def handle_long_lines_text(text, limit=MAX_LINE_LENGTH):
    if not text:
        return ""
    output = []
    lines = text.splitlines()
    for line in lines:
        if len(line) < limit:
            output.append(line)
        else:
            next_line = ""
            words = line.split()
            for word in words:
                if len(next_line) + len(word) > limit:
                    output.append(next_line)
                    next_line = word
                else:
                    next_line += (" " if len(next_line) else "") + word

            if next_line:
                output.append(next_line)
    return "\n".join(output)


def handle_long_lines_html(html):
    lines = html.splitlines()
    if not any([len(line) > MAX_LINE_LENGTH for line in lines]):
        return html
    parsed = etree.fromstring(html, parser=etree.HTMLParser())
    etree.indent(parsed, space=" ")  # like pretty print but upfront
    for elem in parsed.iter("*"):
        if elem.text is not None and len(elem.text) > 100:
            elem.text = handle_long_lines_text(elem.text, 100) + "\n"
        if elem.tail is not None and len(elem.tail) > 100:
            elem.tail = handle_long_lines_text(elem.tail, 100) + "\n"
    return etree.tostring(parsed, method="html", encoding="unicode")


@celery.task(soft_time_limit=120)
def _send_email(to, subject, text_body, html_body=None, sender=None, sender_name=None, attachments_info=None):
    if attachments_info is None:
        attachments_info = []

    if sender is None:
        sender = get_app_config("MAIL_DEFAULT_SENDER")

    if sender_name is not None:
        sender = (sender_name, sender)

    decoded_attachments = []
    for a in attachments_info:
        try:
            content = base64.b64decode(a["file"])
            decoded_attachments.append(Attachment(a["file_name"], a["content_type"], data=content))
        except Exception as e:
            logger.error("Error attaching {} file to mail. Receipient(s): {}. Error: {}".format(a["file_desc"], to, e))

    msg = NewsroomMessage(subject=subject, sender=sender, recipients=to, attachments=decoded_attachments)
    msg.body = text_body
    msg.html = html_body
    app = get_current_app().as_any()
    return app.mail.send(msg)


def send_email(to, subject, text_body, html_body=None, sender=None, sender_name=None, attachments_info=None):
    """
    Sends the email
    :param to: List of recipients
    :param subject: Subject text
    :param text_body: Text Body
    :param html_body: Html Body
    :param sender: Sender
    :return:
    """

    kwargs = {
        "to": to,
        "subject": subject,
        "text_body": handle_long_lines_text(text_body) if text_body else None,
        "html_body": handle_long_lines_html(html_body) if html_body else None,
        "sender": sender,
        "sender_name": sender_name or get_app_config("EMAIL_DEFAULT_SENDER_NAME"),
        "attachments_info": attachments_info,
    }
    _send_email.apply_async(kwargs=kwargs)


async def send_new_signup_email(company: Company, user: User, is_new_company: bool):
    url_kwargs = (
        {
            "app_id": "companies",
            "companyId": str(company["_id"]),
            "_external": True,
        }
        if is_new_company
        else {
            "app_id": "users",
            "userId": str(user["_id"]),
            "_external": True,
        }
    )
    country_name = company.get("country") or ""
    countries: List[Country] = get_current_app().as_any().countries
    if len(country_name) and len(countries):
        country: Optional[Country] = next((c for c in countries if c["value"] == country_name), None)
        if country is not None:
            country_name = country["text"]

    company_type_name = company.get("company_type") or ""
    company_types: List[CompanyType] = get_app_config("COMPANY_TYPES") or []
    if len(company_type_name) and len(company_types):
        company_type: Optional[CompanyType] = next((t for t in company_types if t["id"] == company_type_name), None)
        if company_type is not None:
            company_type_name = company_type["name"]

    await send_template_email(
        to=get_app_config("SIGNUP_EMAIL_RECIPIENTS").split(","),
        template="signup_request_email",
        template_kwargs=dict(
            url=url_for("settings.settings_app", **url_kwargs),
            user=user,
            company=company,
            is_new_company=is_new_company,
            country=country_name,
            company_type=company_type_name,
        ),
    )


def map_email_recipients_by_language(
    emails: List[str], template_name: str, ignore_preferences=False
) -> Dict[str, EmailGroup]:
    users = {user["email"]: user for user in get_resource_service("users").find(where={"email": {"$in": emails}}) or []}
    default_language = get_app_config("DEFAULT_LANGUAGE")
    groups: Dict[str, EmailGroup] = {}
    default_html_template = get_language_template_name(template_name, default_language, "html")
    default_txt_template = get_language_template_name(template_name, default_language, "txt")

    for email in emails:
        user = users.get(email)
        if user and not user.get("receive_email") and not ignore_preferences:
            # If this is a user in the system, and has emails disabled
            # then skip this recipient
            continue

        email_language = to_email_language((user or {}).get("locale") or default_language)
        html_template_name = get_language_template_name(template_name, email_language, "html")
        text_template = get_language_template_name(template_name, email_language, "txt")

        if html_template_name == default_html_template and text_template == default_txt_template:
            email_language = default_language

        if not groups.get(email_language):
            groups[email_language] = EmailGroup(
                html_template=html_template_name, text_template=text_template, emails=[]
            )

        groups[email_language]["emails"].append(email)

    return groups


def to_email_language(language: str) -> str:
    return language.lower().replace("-", "_")


def get_language_template_name(template_name: str, language: str, extension: str) -> str:
    language_template_name = f"{template_name}.{language}.{extension}"
    fallback_template_name = f"{template_name}.{extension}"

    try:
        get_current_app().jinja_env.get_or_select_template(language_template_name)
        return language_template_name
    except TemplateNotFound:
        pass

    return fallback_template_name


EmailKwargs = Dict[str, Any]
TemplateKwargs = Dict[str, Any]


# TODO-ASYNC: change this to use newsroom.users.model.UserResourceModel only
async def send_user_email(
    user: Union[User, "UserResourceModel"],
    template: str,
    template_kwargs: Optional[TemplateKwargs] = None,
    ignore_preferences=False,  # ignore user email preferences
    **kwargs: EmailKwargs,
) -> None:
    """Send an email to Newsroom user, respecting user's email preferences."""
    if isinstance(user, ResourceModel):
        user = user.to_dict()

    if not user.get("receive_email") and not ignore_preferences:
        # If this is a user in the system, and has emails disabled
        # then skip this recipient
        return

    language = user.get("locale") or get_app_config("DEFAULT_LANGUAGE")
    timezone = get_user_timezone(user)
    await _send_localized_email([user["email"]], template, language, timezone, template_kwargs or {}, kwargs)


async def send_template_email(
    to: List[str],
    template: str,
    template_kwargs: Optional[TemplateKwargs] = None,
    **kwargs: EmailKwargs,
) -> None:
    """Send email to list of recipients using default locale."""
    language = get_app_config("DEFAULT_LANGUAGE")
    timezone = get_app_config("DEFAULT_TIMEZONE")
    await _send_localized_email(to, template, language, timezone, template_kwargs or {}, kwargs)


async def _send_localized_email(
    to: List[str],
    template: str,
    language: str,
    timezone: str,
    template_kwargs: TemplateKwargs,
    email_kwargs: EmailKwargs,
) -> None:
    language = to_email_language(language)
    email_templates = get_resource_service("email_templates")
    html_template = get_language_template_name(template, language, "html")
    text_template = get_language_template_name(template, language, "txt")
    with template_locale(language, timezone):
        subject = await email_templates.get_translated_subject(template, language, **template_kwargs)
        template_kwargs.setdefault("subject", subject)
        template_kwargs.setdefault("recipient_language", language)

        text_body = await render_template(text_template, **template_kwargs)
        html_body = await render_template(html_template, **template_kwargs)

        send_email(
            to=to,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            sender_name=get_sender_name(language),
            **email_kwargs,
        )


def get_sender_name(language: str) -> Optional[str]:
    try:
        return get_app_config("EMAIL_SENDER_NAME_LANGUAGE_MAP")[language]
    except (KeyError, TypeError):
        return None


async def send_validate_account_email(user: User, token: str) -> None:
    """
    Forms and sends validation email
    :param user_name: Name of the user
    :param user_email: Email address
    :param token: token string
    :return:
    """
    app_name = get_app_config("SITE_NAME")
    url = url_for("auth.validate_account", token=token, _external=True)
    hours = get_app_config("VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE") * 24

    await send_user_email(
        user,
        template="validate_account_email",
        template_kwargs=dict(
            app_name=app_name,
            name=user.get("first_name"),
            expires=hours,
            url=url,
        ),
        ignore_preferences=True,
    )


async def send_new_account_email(user: User, token: str) -> None:
    """
    Forms and sends validation email
    :param user_name: Name of the user
    :param user_email: Email address
    :param token: token string
    :return:
    """
    app_name = get_app_config("SITE_NAME")
    url = url_for("auth.reset_password", token=token, _external=True)
    hours = get_app_config("VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE") * 24

    await send_user_email(
        user,
        template="account_created_email",
        template_kwargs=dict(
            app_name=app_name,
            name=user.get("first_name"),
            expires=hours,
            url=url,
        ),
        ignore_preferences=True,
    )


async def send_reset_password_email(user: User, token: str) -> None:
    """
    Forms and sends reset password email
    :param user_name: Name of the user
    :param user_email: Email address
    :param token: token string
    :return:
    """
    app_name = get_app_config("SITE_NAME")
    url = url_for("auth.reset_password", token=token, _external=True)
    hours = get_app_config("RESET_PASSWORD_TOKEN_TIME_TO_LIVE") * 24

    await send_user_email(
        user=user,
        template="reset_password_email",
        template_kwargs=dict(
            app_name=app_name,
            name=user.get("first_name"),
            email=user["email"],
            expires=hours,
            url=url,
        ),
        ignore_preferences=True,
    )


async def send_new_item_notification_email(user, topic_name, item, section="wire"):
    if item.get("type") == "text":
        await _send_new_wire_notification_email(user, topic_name, item, section)
    else:
        await _send_new_agenda_notification_email(user, topic_name, item)


async def _send_new_wire_notification_email(user, topic_name, item, section):
    url = url_for("wire.item", _id=item.get("guid") or item["_id"], _external=True)
    template_kwargs = dict(
        app_name=get_app_config("SITE_NAME"),
        is_topic=True,
        topic_name=topic_name,
        name=user.get("first_name"),
        item=item,
        url=url,
        type="wire",
        section=section,
    )
    await send_user_email(
        user,
        template="new_wire_notification_email",
        template_kwargs=template_kwargs,
    )


def _remove_restricted_coverage_info(item):
    # Import here to prevent circular imports
    from newsroom.auth.utils import get_company_or_none_from_request
    from newsroom.agenda.utils import remove_restricted_coverage_info

    company = get_company_or_none_from_request(None)
    if company and company.restrict_coverage_info:
        remove_restricted_coverage_info([item])


async def _send_new_agenda_notification_email(user, topic_name, item):
    _remove_restricted_coverage_info(item)
    url = url_for_agenda(item, _external=True)
    template_kwargs = dict(
        app_name=get_app_config("SITE_NAME"),
        is_topic=True,
        topic_name=topic_name,
        name=user.get("first_name"),
        item=item,
        url=url,
        type="agenda",
        dateString=get_agenda_dates(item),
        location=get_location_string(item),
        contacts=get_public_contacts(item),
        links=get_links(item),
        is_admin=is_admin_or_internal(user),
        section="agenda",
    )
    await send_user_email(
        user=user,
        template="new_agenda_notification_email",
        template_kwargs=template_kwargs,
    )


async def send_history_match_notification_email(user, item, section):
    if item.get("type") == "text":
        await _send_history_match_wire_notification_email(user, item, section)
    else:
        await _send_history_match_agenda_notification_email(user, item)


async def _send_history_match_wire_notification_email(user, item, section):
    app_name = get_app_config("SITE_NAME")
    url = url_for("wire.item", _id=item.get("guid") or item["_id"], _external=True)
    template_kwargs = dict(
        app_name=app_name,
        is_topic=False,
        name=user.get("first_name"),
        item=item,
        url=url,
        type="wire",
        section=section,
    )
    await send_user_email(
        user,
        template="updated_wire_notification_email",
        template_kwargs=template_kwargs,
    )


async def _send_history_match_agenda_notification_email(user, item):
    _remove_restricted_coverage_info(item)
    app_name = get_app_config("SITE_NAME")
    url = url_for_agenda(item, _external=True)
    template_kwargs = dict(
        app_name=app_name,
        is_topic=False,
        name=user.get("first_name"),
        item=item,
        url=url,
        type="agenda",
        dateString=get_agenda_dates(item),
        location=get_location_string(item),
        contacts=get_public_contacts(item),
        links=get_links(item),
        is_admin=is_admin_or_internal(user),
        section="agenda",
    )
    await send_user_email(
        user,
        template="updated_agenda_notification_email",
        template_kwargs=template_kwargs,
    )


async def send_item_killed_notification_email(user, item):
    if item.get("type") == "text":
        await _send_wire_killed_notification_email(user, item)
    else:
        await _send_agenda_killed_notification_email(user, item)


async def _send_wire_killed_notification_email(user, item):
    formatter = get_current_app().as_any().download_formatters["text"]["formatter"]
    recipients = [user["email"]]
    subject = gettext("Kill/Takedown notice")
    text_body = to_text(await formatter.format_item(item))

    send_email(to=recipients, subject=subject, text_body=text_body)


async def _send_agenda_killed_notification_email(user, item):
    formatter = get_current_app().as_any().download_formatters["text"]["formatter"]
    recipients = [user["email"]]
    subject = gettext("%(section)s cancelled notice", section=get_app_config("AGENDA_SECTION"))
    text_body = to_text(await formatter.format_item(item, item_type="agenda"))

    send_email(to=recipients, subject=subject, text_body=text_body)


def to_text(output: Union[str, bytes]) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8")
    return output
