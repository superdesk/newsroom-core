from flask import current_app
from .cli import newsroom_cli


@newsroom_cli.cli.command("content_reset")
def content_reset():
    """Removes all data from 'items' and 'items_versions' indexes/collections.

    Example:
    ::

        $ python manage.py content_reset

    """
    current_app.data.remove("items")
    current_app.data.remove("items_versions")
