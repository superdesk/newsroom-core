from newsroom.wire import WireSearchServiceAsync

from .cli import newsroom_cli


@newsroom_cli.command("content_reset")
async def content_reset():
    """Removes all data from 'items' and 'items_versions' indexes/collections.

    Example:
    ::

        $ python manage.py content_reset

    """
    await WireSearchServiceAsync().service.delete_many({})
