import click
from quart.cli import with_appcontext

from newsroom.notifications.send_scheduled_notifications import SendScheduledNotificationEmails
from .cli import newsroom_cli


@newsroom_cli.command("send_scheduled_notifications")
@click.option(
    "-i",
    "--ignore-schedule",
    "force",
    is_flag=True,
    required=False,
    help="Runs a schedule if one has not been run for that user's schedule",
)
@with_appcontext
def send_scheduled_notifications(force=False):
    """
    Send scheduled notifications

    Example:
    ::

        $ python manage.py send_scheduled_notifications
    """
    SendScheduledNotificationEmails().run(force)
