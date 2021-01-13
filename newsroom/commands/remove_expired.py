import content_api

from .manager import app, manager


@manager.option('-m', '--expiry', dest='expiry_days', required=False)
def remove_expired(expiry_days):
    """Remove expired items from the content_api items collection.

    By default no items expire there, you can change it using ``CONTENT_API_EXPIRY_DAYS`` config.

    Example:
    ::

        $ python manage.py remove_expired

    """
    exp = content_api.RemoveExpiredItems()
    exp.run(expiry_days)
