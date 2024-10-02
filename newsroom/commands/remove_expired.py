import click
import content_api

from .cli import newsroom_cli


@newsroom_cli.command("remove_expired")
@click.option("-m", "--expiry", "expiry_days", required=False, help="Number of days to determine expiry")
def _remove_expired(expiry_days):
    remove_expired(expiry_days)


def remove_expired(expiry_days):
    """Remove expired items from the content_api items collection.

    By default no items expire there, you can change it using ``CONTENT_API_EXPIRY_DAYS`` config.

    Example:
    ::

        $ flask newsroom remove_expired

    """
    exp = content_api.RemoveExpiredItems()
    exp.run(expiry_days)
