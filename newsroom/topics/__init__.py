import flask
import superdesk

from .topics import get_user_topics  # noqa
from . import folders, topics


blueprint = flask.Blueprint("topics", __name__)


def init_app(app):
    topics.topics_service = topics.TopicsService("topics", superdesk.get_backend())
    topics.TopicsResource("topics", app, topics.topics_service)

    superdesk.register_resource("topic_folders", folders.FoldersResource, folders.FoldersService, _app=app)
    superdesk.register_resource("user_topic_folders", folders.UserFoldersResource, folders.UserFoldersService, _app=app)
    superdesk.register_resource(
        "company_topic_folders", folders.CompanyFoldersResource, folders.CompanyFoldersService, _app=app
    )


def get_user_folders(user, section):
    return list(
        superdesk.get_resource_service("user_topic_folders").get(
            req=None,
            lookup={
                "user": user["_id"],
                "section": section,
            },
        )
    )


def get_company_folders(company, section):
    return list(
        superdesk.get_resource_service("company_topic_folders").get(
            req=None,
            lookup={
                "company": company["_id"],
                "section": section,
            },
        )
    )

from . import views  # noqa
