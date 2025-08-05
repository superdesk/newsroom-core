import click
import content_api

from .cli import newsroom_cli


@newsroom_cli.command("remove_expired")
@click.option("-m", "--expiry", "expiry_days", required=False, help="Number of days to determine expiry")
async def remove_expired_command(expiry_days):
    await remove_expired(expiry_days)


async def remove_expired(expiry_days):
    """Remove expired items from the content_api items collection.

    By default no items expire there, you can change it using ``CONTENT_API_EXPIRY_DAYS`` config.

    Example:
    ::

        $ python manage.py remove_expired

    """
    # TODO-ASYNC: Revisit when `RemoveExpiredItems` is update in superdesk-core
    # as it depends on items which is not yet an async resource on SD
    exp = content_api.RemoveExpiredItems()
    exp.run(expiry_days)
