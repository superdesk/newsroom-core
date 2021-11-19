import flask
import superdesk

from superdesk.notification import push_notification  # noqa
from newsroom.auth import get_user, get_user_id

blueprint = flask.Blueprint('notifications', __name__)


def push_user_notification(name, **kwargs):
    push_notification(':'.join(map(str, [name, get_user_id()])), **kwargs)


def push_company_notification(name, **kwargs):
    company_id = get_user().get('company')
    push_notification(f'{name}:company-{company_id}', **kwargs)


from .notifications import NotificationsResource, NotificationsService, get_user_notifications  # noqa


def init_app(app):
    superdesk.register_resource('notifications', NotificationsResource, NotificationsService, _app=app)
