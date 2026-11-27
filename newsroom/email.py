from typing import List, Optional, Dict, Any, Union, TypedDict

from quart_babel import gettext
from jinja2 import TemplateNotFound

from superdesk import get_resource_service
from superdesk.core import get_config, get_current_app
from superdesk.core.resources import ResourceModel
from superdesk.core.emails import EmailFactory, EmailAttachment, EmailRequest, EmailAddress
from superdesk.flask import render_template, url_for

from newsroom.gettext import get_user_timezone
from newsroom.types import Company, User, Country, CompanyType, UserResourceModel
from newsroom.formatters import get_formatter
from newsroom.template_loaders import template_locale
from newsroom.utils import (
    get_agenda_dates,
    get_location_string,
    get_links,
    get_public_contacts,
    url_for_agenda,
)
from newsroom.template_filters import is_admin_or_internal


class EmailGroup(TypedDict):
    html_template: str
    text_template: str
    emails: List[str]


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
    company_types: List[CompanyType] = get_config(list[CompanyType], "COMPANY_TYPES", [])
    if len(company_type_name) and len(company_types):
        company_type: Optional[CompanyType] = next((t for t in company_types if t["id"] == company_type_name), None)
        if company_type is not None:
            company_type_name = company_type["name"]

    await send_template_email(
        to=get_config(str, "SIGNUP_EMAIL_RECIPIENTS").split(","),
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
    default_language = get_config(str, "DEFAULT_LANGUAGE")
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


TemplateKwargs = Dict[str, Any]


# TODO-ASYNC: change this to use newsroom.users.model.UserResourceModel only
async def send_user_email(
    user: User | UserResourceModel,
    template: str,
    template_kwargs: Optional[TemplateKwargs] = None,
    ignore_preferences=False,  # ignore user email preferences
    sender: EmailAddress | None = None,
    attachments: list[EmailAttachment] | None = None,
) -> None:
    """Send an email to Newsroom user, respecting user's email preferences."""
    user_dict: User = user.to_dict() if isinstance(user, ResourceModel) else user

    if (not user_dict.get("receive_email") and not ignore_preferences) or (not user_dict.get("is_enabled")):
        # skip user if has emails disabled or the user is not enabled
        return

    language = user_dict.get("locale") or get_config(str, "DEFAULT_LANGUAGE")
    timezone = get_user_timezone(user_dict)
    await _send_localized_email([user_dict["email"]], template, language, timezone, template_kwargs or {}, sender, attachments)


async def send_template_email(
    to: List[str],
    template: str,
    template_kwargs: Optional[TemplateKwargs] = None,
    cc: Optional[List[str]] = None,
    sender: EmailAddress | None = None,
    attachments: list[EmailAttachment] | None = None,
) -> None:
    """Send email to list of recipients using default locale."""
    language = get_config(str, "DEFAULT_LANGUAGE")
    timezone = get_config(str, "DEFAULT_TIMEZONE")
    await _send_localized_email(to, template, language, timezone, template_kwargs or {}, sender, attachments, cc)


async def _send_localized_email(
    to: List[str],
    template: str,
    language: str,
    timezone: str,
    template_kwargs: TemplateKwargs,
    sender: EmailAddress | None = None,
    attachments: list[EmailAttachment] | None = None,
    cc: Optional[List[str]] = None,
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

        mail = EmailFactory()
        await mail.send(
            EmailRequest(
                subject=subject,
                sender=mail.get_address(sender, get_sender_name(language)) if isinstance(sender, str) else sender,
                recipients=to,
                cc=cc,
                text_body=text_body,
                html_body=html_body,
                attachments=attachments,
            )
        )


def get_sender_name(language: str) -> Optional[str]:
    try:
        return get_config(dict[str, str], "EMAIL_SENDER_NAME_LANGUAGE_MAP", {})[language]
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
    app_name = get_config(str, "SITE_NAME")
    url = url_for("auth.validate_account", token=token, _external=True)
    hours = get_config(int, "VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE_HOURS")

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
    app_name = get_config(str, "SITE_NAME")
    url = url_for("auth.reset_password", token=token, _external=True)
    hours = get_config(int, "VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE_HOURS")

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
    app_name = get_config(str, "SITE_NAME")
    url = url_for("auth.reset_password", token=token, _external=True)
    hours = get_config(int, "RESET_PASSWORD_TOKEN_TIME_TO_LIVE_HOURS")

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


# TODO-ASYNC: change this to use newsroom.users.model.UserResourceModel only
async def send_new_item_notification_email(
    user: User | UserResourceModel, topic_name: str, item: dict[str, Any], section: str = "wire"
):
    if item.get("type") == "text":
        await _send_new_wire_notification_email(user, topic_name, item, section)
    else:
        await _send_new_agenda_notification_email(user, topic_name, item)


# TODO-ASYNC: change this to use newsroom.users.model.UserResourceModel only
async def _send_new_wire_notification_email(
    user: User | UserResourceModel, topic_name: str, item: dict[str, Any], section: str
):
    user_dict: User = user.to_dict() if isinstance(user, ResourceModel) else user

    url = url_for("wire.item", item_id=item.get("guid") or item["_id"], _external=True)
    template_kwargs = dict(
        app_name=get_config(str, "SITE_NAME"),
        is_topic=True,
        topic_name=topic_name,
        name=user_dict.get("first_name"),
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


# TODO-ASYNC: change this to use newsroom.users.model.UserResourceModel only
async def _send_new_agenda_notification_email(user: User | UserResourceModel, topic_name: str, item: dict[str, Any]):
    # Import here to prevent circular imports
    from newsroom.agenda.utils import get_related_events

    user_dict: User = user.to_dict() if isinstance(user, ResourceModel) else user
    related_events = await get_related_events(item)
    _remove_restricted_coverage_info(item)
    url = url_for_agenda(item, _external=True)
    template_kwargs = dict(
        app_name=get_config(str, "SITE_NAME"),
        is_topic=True,
        topic_name=topic_name,
        name=user_dict.get("first_name"),
        item=item,
        url=url,
        type="agenda",
        dateString=get_agenda_dates(item),
        location=get_location_string(item),
        contacts=get_public_contacts(item),
        links=get_links(item),
        is_admin=is_admin_or_internal(user),
        section="agenda",
        related_events=related_events,
    )
    await send_user_email(
        user=user,
        template="new_agenda_notification_email",
        template_kwargs=template_kwargs,
    )


async def send_history_match_notification_email(user: UserResourceModel, item: dict[str, Any], section: str) -> None:
    if item.get("type") == "text":
        await _send_history_match_wire_notification_email(user, item, section)
    else:
        await _send_history_match_agenda_notification_email(user, item)


async def _send_history_match_wire_notification_email(
    user: UserResourceModel, item: dict[str, Any], section: str
) -> None:
    app_name = get_config(str, "SITE_NAME")
    url = url_for("wire.item", item_id=item.get("guid") or item["_id"], _external=True)
    template_kwargs = dict(
        app_name=app_name,
        is_topic=False,
        name=user.first_name,
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


async def _send_history_match_agenda_notification_email(user: UserResourceModel, item: dict[str, Any]):
    _remove_restricted_coverage_info(item)
    app_name = get_config(str, "SITE_NAME")
    url = url_for_agenda(item, _external=True)
    template_kwargs = dict(
        app_name=app_name,
        is_topic=False,
        name=user.first_name,
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


async def send_item_killed_notification_email(user: UserResourceModel, item: dict[str, Any]) -> None:
    if item.get("type") == "text":
        await _send_wire_killed_notification_email(user, item)
    else:
        await _send_agenda_killed_notification_email(user, item)


async def _send_wire_killed_notification_email(user: UserResourceModel, item: dict[str, Any]) -> None:
    formatter = get_formatter("text")
    recipients = [user.email]
    subject = gettext("Kill/Takedown notice")
    text_body = to_text(await formatter.format_item(item))

    await EmailFactory().send(
        EmailRequest(subject=subject, recipients=recipients, text_body=text_body)
    )


async def _send_agenda_killed_notification_email(user: UserResourceModel, item: dict[str, Any]) -> None:
    formatter = get_formatter("text")
    recipients = [user.email]
    subject = gettext("%(section)s cancelled notice", section=get_config(str, "AGENDA_SECTION"))
    text_body = to_text(await formatter.format_item(item, item_type="agenda"))

    await EmailFactory().send(
        EmailRequest(subject=subject, recipients=recipients, text_body=text_body)
    )


def to_text(output: Union[str, bytes]) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8")
    return output
