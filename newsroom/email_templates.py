from typing import Optional
import logging

from flask import render_template_string, current_app
from flask_babel import gettext
from werkzeug.exceptions import BadRequest, NotFound
from eve.utils import config

from superdesk import Resource, Service, register_resource

logger = logging.getLogger(__name__)
RESOURCE = "email_templates"


class EmailTemplatesResource(Resource):
    endpoint_name = RESOURCE
    item_methods = ["GET"]
    resource_methods = ["GET"]
    datasource = {"source": RESOURCE}
    schema = {
        # Identifies the email template these translations are used for
        "_id": {
            "type": "string",
            "unique": True,
            "required": True,
            "nullable": False,
            "empty": False,
        },
        "subject": {
            "type": "dict",
            "schema": {"default": {"type": "string"}, "translations": {"type": "dict"}},
        },
    }


DEFAULT_SUBJECTS = {
    "agenda_new_coverage_email": "New coverage",
    "agenda_updated_email": "{{ agenda.name or agenda.headline or agenda.slugline | safe }}"
    " -{{ ' Coverage' if coverage_modified else '' }} updated",
    "coverage_request_email": "Coverage inquiry: {{ item.name or item.slugline | safe }}",
    "company_expiry_alert_user": "Your Company's account is expiring on {{ expires_on }}",
    "company_expiry_email": "Companies expired or due to expire within the next 7 days ({{ expires_on }})",
    "signup_request_email": "A new Newshub signup request",
    "validate_account_email": "{{ app_name }} account created",
    "account_created_email": "{{ app_name }} account created",
    "reset_password_email": "{{ app_name }} password reset",
    "new_wire_notification_email": "New story for followed topic: {{ topic_name | safe }}",
    "new_agenda_notification_email": "New update for followed agenda: {{ topic_name | safe }}",
    "updated_wire_notification_email": "New update for your previously accessed story {{ item.headline | safe }}",
    "updated_agenda_notification_email": "New update for your previously accessed agenda {{ item.name | safe }}",
    "monitoring_email": "{% if profile.headline_subject and items | length == 1 %}"
    "{{ items[0].headline or profile.subject or profile.name | safe }}"
    "{% else %}"
    "{{ profile.subject or profile.name | safe }}"
    "{% endif %}",
    "monitoring_error": "Error sending alerts for monitoring: {{ profile.name | safe }}",
    "monitoring_email_no_updates": "{{ profile.subject or profile.name | safe }}",
    "share_items": "From {{ app_name }}: {{ subject_name | safe }}",
    "share_topic": "From {{ app_name }}: {{ topic.label | safe }}",
    "share_wire": "From {{ app_name }}: {{ subject_name | safe }}",
    "share_agenda": "From {{ app_name }}: {{ subject_name | safe }}",
    "additional_product_seat_request_email": "New Product Seat request",
}


class EmailTemplatesService(Service):
    def find_one(self, req, **lookup):
        email = super().find_one(req, **lookup)

        if not email:
            email_id = lookup.get(config.ID_FIELD)

            if not email_id:
                raise BadRequest(gettext("Email template name not supplied"))
            elif not DEFAULT_SUBJECTS.get(email_id):
                raise NotFound(gettext("Email template '%(name)s' not found", name=email_id))

            email = {"_id": email_id}

        self.enhance_items([email])
        return email

    def on_fetched(self, doc):
        self.enhance_items(doc[config.ITEMS])

    def on_fetched_item(self, doc):
        self.enhance_items([doc])

    def enhance_items(self, docs):
        for email in docs:
            email_id = email["_id"]
            email.setdefault("subject", {})
            email["subject"].setdefault("default", DEFAULT_SUBJECTS[email_id])
            email["subject"].setdefault("translations", {})

    def get_translated_subject(self, email_id: str, language_code: Optional[str] = None, **kwargs) -> str:
        language_code = language_code or current_app.config["DEFAULT_LANGUAGE"]
        email = self.find_one(req=None, _id=email_id)

        try:
            subject = email["subject"]["translations"][language_code.lower()]
        except (KeyError, AttributeError):
            subject = email["subject"]["default"]

        try:
            return render_template_string(subject, **kwargs)
        except Exception as ex:
            if subject == email["subject"]["default"]:
                logger.error("Failed to render email subject")
                logger.exception(ex)
                raise

        try:
            # If the rendering fails, assume it is an error with the translation template
            # and fallback to using the default template
            logger.warning("Failed to render custom email subject, reverting to default instead")
            subject = email["subject"]["default"]
            return render_template_string(subject, **kwargs)
        except Exception as ex:
            logger.error("Failed to render email subject using default template")
            logger.exception(ex)
            raise


def init_app(app):
    register_resource(RESOURCE, EmailTemplatesResource, EmailTemplatesService, _app=app)
