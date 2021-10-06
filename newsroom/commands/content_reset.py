from .manager import app, manager


@manager.command
def content_reset():
    """Removes all data from 'items' and 'items_versions' indexes/collections.

    Example:
    ::

        $ python manage.py content_reset

    """
    app.data.remove('items')
    app.data.remove('items_versions')
