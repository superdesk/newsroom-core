from newsroom.notifications.send_scheduled_notifications import SendScheduledNotificationEmails

from .manager import manager


@manager.option(
    "-i",
    "--ignore-schedule",
    dest="force",
    required=False,
    action="store_true",
    help="Runs a schedule if one has not been run for that users schedule",
)
@manager.command
def send_scheduled_notifications(force=False):
    """
    Send scheduled notifications

    Example:
    ::

        $ python manage.py send_scheduled_notifications
    """
    SendScheduledNotificationEmails().run(force)
