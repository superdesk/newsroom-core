import base64
import email.policy as email_policy

from lxml import etree
from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict

from superdesk import get_resource_service
from flask import current_app, render_template, url_for
from flask_babel import gettext
from flask_mail import Attachment, Message
from jinja2 import TemplateNotFound

from newsroom.celery_app import celery
from newsroom.utils import get_agenda_dates, get_location_string, get_links, \
    get_public_contacts
from newsroom.template_filters import is_admin_or_internal
from newsroom.utils import url_for_agenda, query_resource
from superdesk.logging import logger


class NewsroomMessage(Message):
    def _message(self):
        msg = super()._message()
        msg.policy = email_policy.SMTPUTF8
        return msg


class EmailGroup(TypedDict):
    html_template: str
    text_template: str
    emails: List[str]


MAX_LINE_LENGTH = 998 - 50  # RFC 5322 - buffer for html indentation


def handle_long_lines_text(text):
    if not text:
        return text
    output = []
    lines = text.splitlines()
    for line in lines:
        if len(line) < MAX_LINE_LENGTH:
            output.append(line)
        else:
            next_line = ''
            words = line.split()
            for word in words:
                if len(next_line) + len(word) > MAX_LINE_LENGTH:
                    output.append(next_line)
                    next_line = word
                else:
                    next_line += (' ' if len(next_line) else '') + word

            if next_line:
                print("IN", next_line)
                output.append(next_line)
    return "\n".join(output)


def handle_long_lines_html(html):
    lines = html.splitlines()
    if not any([len(line) > MAX_LINE_LENGTH for line in lines]):
        return html
    parsed = etree.fromstring(html, parser=etree.HTMLParser())
    etree.indent(parsed, space=" ")  # like pretty print but upfront
    for elem in parsed.iter():
        if elem.text is not None and len(elem.text) > MAX_LINE_LENGTH:
            elem.text = handle_long_lines_text(elem.text) + "\n"
        if elem.tail is not None and len(elem.tail) > MAX_LINE_LENGTH:
            elem.tail = handle_long_lines_text(elem.tail) + "\n"
    return etree.tostring(parsed, method="html", encoding="unicode")


@celery.task(soft_time_limit=120)
def _send_email(to, subject, text_body, html_body=None, sender=None, attachments_info=None):
    if attachments_info is None:
        attachments_info = []

    if sender is None:
        sender = current_app.config['MAIL_DEFAULT_SENDER']

    decoded_attachments = []
    for a in attachments_info:
        try:
            content = base64.b64decode(a['file'])
            decoded_attachments.append(Attachment(a['file_name'],
                                                  a['content_type'], data=content))
        except Exception as e:
            logger.error('Error attaching {} file to mail. Receipient(s): {}. Error: {}'.format(
                a['file_desc'], to, e))

    msg = NewsroomMessage(subject=subject, sender=sender, recipients=to, attachments=decoded_attachments)
    msg.body = text_body
    msg.html = html_body
    app = current_app._get_current_object()
    with app.mail.connect() as connection:
        if connection:
            return connection.send(msg)

        return app.mail.send(msg)


def send_email(to, subject, text_body, html_body=None, sender=None, attachments_info=None):
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
        'to': to,
        'subject': subject,
        'text_body': handle_long_lines_text(text_body),
        'html_body': handle_long_lines_html(html_body),
        'sender': sender,
        'attachments_info': attachments_info,
    }
    _send_email.apply_async(kwargs=kwargs)


def send_new_signup_email(user):
    send_template_email(
        to=current_app.config["SIGNUP_EMAIL_RECIPIENTS"].split(","),
        template="signup_request_email",
        template_kwargs=dict(
            url=url_for("settings.app", app_id="users", _external=True),
            user=user,
        ),
    )


def map_email_recipients_by_language(emails: List[str], template_name: str) -> Dict[str, EmailGroup]:
    users = {
        user["email"]: user
        for user in query_resource("users", lookup={"email": {"$in": emails}}) or []
    }
    default_language = current_app.config["DEFAULT_LANGUAGE"]
    groups: Dict[str, EmailGroup] = {}
    default_html_template = get_language_template_name(template_name, default_language, "html")
    default_txt_template = get_language_template_name(template_name, default_language, "txt")

    for email in emails:
        user = users.get(email)
        if user and not user.get("receive_email"):
            # If this is a user in the system, and has emails disabled
            # then skip this recipient
            continue

        email_language = ((user or {}).get("locale") or default_language).lower().replace("-", "_")
        html_template_name = get_language_template_name(template_name, email_language, "html")
        text_template = get_language_template_name(template_name, email_language, "txt")

        if html_template_name == default_html_template and text_template == default_txt_template:
            email_language = default_language

        if not groups.get(email_language):
            groups[email_language] = EmailGroup(
                html_template=html_template_name,
                text_template=text_template,
                emails=[]
            )

        groups[email_language]["emails"].append(email)

    return groups


def get_language_template_name(template_name: str, language: str, extension: str) -> str:
    language_template_name = f"{template_name}.{language}.{extension}"
    fallback_template_name = f"{template_name}.{extension}"

    try:
        current_app.jinja_env.get_or_select_template(language_template_name)
        return language_template_name
    except TemplateNotFound:
        pass

    return fallback_template_name


def send_template_email(
    to: List[str],
    template: str,
    template_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs
):
    template_kwargs = {} if not template_kwargs else template_kwargs
    email_templates = get_resource_service("email_templates")
    for language, group in map_email_recipients_by_language(to, template).items():
        # ``coverage_request_email`` requires ``subject`` variable for the body template
        # so add the generated/rendered subject to kwargs (if subject is not already defined)
        subject = email_templates.get_translated_subject(template, language, **template_kwargs)
        template_kwargs.setdefault("subject", subject)
        template_kwargs.setdefault("recipient_language", language)

        send_email(
            to=group["emails"],
            subject=subject,
            text_body=render_template(group["text_template"], **template_kwargs),
            html_body=render_template(group["html_template"], **template_kwargs),
            **kwargs
        )


def send_validate_account_email(user_name, user_email, token):
    """
    Forms and sends validation email
    :param user_name: Name of the user
    :param user_email: Email address
    :param token: token string
    :return:
    """
    app_name = current_app.config['SITE_NAME']
    url = url_for('auth.validate_account', token=token, _external=True)
    hours = current_app.config['VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE'] * 24

    send_template_email(
        to=[user_email],
        template="validate_account_email",
        template_kwargs=dict(
            app_name=app_name,
            name=user_name,
            expires=hours,
            url=url,
        ),
    )


def send_new_account_email(user_name, user_email, token):
    """
    Forms and sends validation email
    :param user_name: Name of the user
    :param user_email: Email address
    :param token: token string
    :return:
    """
    app_name = current_app.config['SITE_NAME']
    url = url_for('auth.reset_password', token=token, _external=True)
    hours = current_app.config['VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE'] * 24

    send_template_email(
        to=[user_email],
        template="account_created_email",
        template_kwargs=dict(
            app_name=app_name,
            name=user_name,
            expires=hours,
            url=url,
        )
    )


def send_reset_password_email(user_name, user_email, token):
    """
    Forms and sends reset password email
    :param user_name: Name of the user
    :param user_email: Email address
    :param token: token string
    :return:
    """
    app_name = current_app.config['SITE_NAME']
    url = url_for('auth.reset_password', token=token, _external=True)
    hours = current_app.config['RESET_PASSWORD_TOKEN_TIME_TO_LIVE'] * 24

    send_template_email(
        to=[user_email],
        template="reset_password_email",
        template_kwargs=dict(
            app_name=app_name,
            name=user_name,
            email=user_email,
            expires=hours,
            url=url,
        ),
    )


def send_new_item_notification_email(user, topic_name, item, section='wire'):
    if item.get('type') == 'text':
        _send_new_wire_notification_email(user, topic_name, item, section)
    else:
        _send_new_agenda_notification_email(user, topic_name, item)


def _send_new_wire_notification_email(user, topic_name, item, section):
    url = url_for('wire.item', _id=item['guid'], _external=True)
    recipients = [user['email']]
    template_kwargs = dict(
        app_name=current_app.config["SITE_NAME"],
        is_topic=True,
        topic_name=topic_name,
        name=user.get("first_name"),
        item=item,
        url=url,
        type="wire",
        section=section,
    )
    send_template_email(
        to=recipients,
        template="new_wire_notification_email",
        template_kwargs=template_kwargs,
    )


def _send_new_agenda_notification_email(user, topic_name, item):
    url = url_for_agenda(item, _external=True)
    recipients = [user['email']]
    template_kwargs = dict(
        app_name=current_app.config["SITE_NAME"],
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
    send_template_email(
        to=recipients,
        template="new_agenda_notification_email",
        template_kwargs=template_kwargs,
    )


def send_history_match_notification_email(user, item, section):
    if item.get('type') == 'text':
        _send_history_match_wire_notification_email(user, item, section)
    else:
        _send_history_match_agenda_notification_email(user, item)


def _send_history_match_wire_notification_email(user, item, section):
    app_name = current_app.config['SITE_NAME']
    url = url_for('wire.item', _id=item['guid'], _external=True)
    recipients = [user['email']]
    template_kwargs = dict(
        app_name=app_name,
        is_topic=False,
        name=user.get("first_name"),
        item=item,
        url=url,
        type="wire",
        section=section,
    )
    send_template_email(
        to=recipients,
        template="updated_wire_notification_email",
        template_kwargs=template_kwargs,
    )


def _send_history_match_agenda_notification_email(user, item):
    app_name = current_app.config['SITE_NAME']
    url = url_for_agenda(item, _external=True)
    recipients = [user['email']]
    template_kwargs = dict(
        app_name=app_name,
        is_topic=False,
        name=user.get('first_name'),
        item=item,
        url=url,
        type='agenda',
        dateString=get_agenda_dates(item),
        location=get_location_string(item),
        contacts=get_public_contacts(item),
        links=get_links(item),
        is_admin=is_admin_or_internal(user),
        section='agenda'
    )
    send_template_email(
        to=recipients,
        template="updated_agenda_notification_email",
        template_kwargs=template_kwargs,
    )


def send_item_killed_notification_email(user, item):
    if item.get('type') == 'text':
        _send_wire_killed_notification_email(user, item)
    else:
        _send_agenda_killed_notification_email(user, item)


def _send_wire_killed_notification_email(user, item):
    formatter = current_app.download_formatters['text']['formatter']
    recipients = [user['email']]
    subject = gettext('Kill/Takedown notice')
    text_body = formatter.format_item(item)

    send_email(to=recipients, subject=subject, text_body=text_body)


def _send_agenda_killed_notification_email(user, item):
    formatter = current_app.download_formatters['text']['formatter']
    recipients = [user['email']]
    subject = gettext('Agenda cancelled notice')
    text_body = formatter.format_item(item, item_type='agenda')

    send_email(to=recipients, subject=subject, text_body=text_body)
