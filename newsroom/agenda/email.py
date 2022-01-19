from newsroom.email import send_template_email
from newsroom.utils import get_agenda_dates, get_location_string, get_links, get_public_contacts, url_for_agenda
from newsroom.template_filters import is_admin_or_internal
from newsroom.settings import get_settings_collection, GENERAL_SETTINGS_LOOKUP
from newsroom.companies import get_user_company


def send_coverage_notification_email(user, agenda, wire_item):
    if user.get('receive_email'):
        template_kwargs = dict(
            agenda=agenda,
            item=wire_item,
            section='agenda',
        )
        send_template_email(
            to=[user["email"]],
            template="agenda_new_coverage_email",
            template_kwargs=template_kwargs,
        )


def send_agenda_notification_email(
    user, agenda, message,
    original_agenda, coverage_updates,
    related_planning_removed, coverage_updated, time_updated,
    coverage_modified
):
    if agenda and user.get('receive_email'):
        template_kwargs = dict(
            message=message,
            agenda=agenda,
            dateString=get_agenda_dates(agenda if agenda.get('dates') else original_agenda, date_paranthesis=True),
            location=get_location_string(agenda),
            contacts=get_public_contacts(agenda),
            links=get_links(agenda),
            is_admin=is_admin_or_internal(user),
            original_agenda=original_agenda,
            coverage_updates=coverage_updates,
            related_planning_removed=related_planning_removed,
            coverage_updated=coverage_updated,
            time_updated=time_updated,
            coverage_modified=coverage_modified,
        )
        send_template_email(
            to=[user["email"]],
            template="agenda_updated_email",
            template_kwargs=template_kwargs,
        )


def send_coverage_request_email(user, message, item):
    """
    Forms and sends coverage request email
    :param user: User that makes the request
    :param message: Request message
    :param item: agenda item that request is made against
    :return:
    """

    general_settings = get_settings_collection().find_one(GENERAL_SETTINGS_LOOKUP)
    if not general_settings:
        return

    recipients = general_settings.get('values').get('coverage_request_recipients').split(',')
    assert recipients
    assert isinstance(recipients, list)
    url = url_for_agenda({'_id': item['_id']}, _external=True)
    name = '{} {}'.format(user.get('first_name'), user.get('last_name'))
    email = user.get('email')

    item_name = item.get('name') or item.get('slugline')
    user_company = get_user_company(user)
    if user_company:
        user_company = user_company.get('name')

    template_kwargs = dict(
        name=name,
        email=email,
        message=message,
        url=url,
        company=user_company,
        recipients=recipients,
        item_name=item_name,
        item=item,
    )

    send_template_email(
        to=recipients,
        template="coverage_request_email",
        template_kwargs=template_kwargs,
    )
