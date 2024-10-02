from superdesk.core import get_current_app

from .cli import newsroom_cli


@newsroom_cli.command("content_reset")
def content_reset():
    """Removes all data from 'items' and 'items_versions' indexes/collections.

    Example:
    ::

        $ python manage.py content_reset

    """
    app = get_current_app()
    app.data.remove("items")
    app.data.remove("items_versions")
