import newsroom
import superdesk

from newsroom.user_roles import UserRole
from newsroom.signals import user_deleted

from . import topics


class FoldersResource(newsroom.Resource):
    resource_title = "topic_folders"
    resource_methods = ["GET"]
    item_methods = ["GET"]
    collation = True
    datasource = {"source": "topic_folders", "default_sort": [("name", 1)]}
    schema = {
        "name": {"type": "string", "required": True},
        "parent": newsroom.Resource.rel("topic_folders", nullable=True),
        "section": {
            "type": "string",
            "required": True,
            "allowed": ["wire", "agenda", "monitoring"],
        },
    }

    mongo_indexes: newsroom.MongoIndexes = {
        "unique_topic_folder_name": (
            [
                ("company", 1),
                ("user", 1),
                ("section", 1),
                ("parent", 1),
                ("name", 1),
            ],
            {"unique": True, "collation": {"locale": "en", "strength": 2}},
        ),
    }
    allowed_roles = [role for role in UserRole]
    allowed_item_roles = allowed_roles


class UserFoldersResource(FoldersResource):
    url = 'users/<regex("[a-f0-9]{24}"):user>/topic_folders'
    regex_url = "users/([a-f0-9]{24})/topic_folders"
    resource_title = "user_topic_folders"
    resource_methods = ["GET", "POST"]
    item_methods = ["GET", "PATCH", "DELETE"]
    schema = FoldersResource.schema.copy()
    schema.update(
        {
            "user": newsroom.Resource.rel("users", required=True),
        }
    )


class CompanyFoldersResource(FoldersResource):
    url = 'companies/<regex("[a-f0-9]{24}"):company>/topic_folders'
    regex_url = "companies/([a-f0-9]{24})/topic_folders"
    resource_title = "company_topic_folders"
    resource_methods = ["GET", "POST"]
    item_methods = ["GET", "PATCH", "DELETE"]
    schema = FoldersResource.schema.copy()
    schema.update(
        {
            "company": newsroom.Resource.rel("companies", required=True),
        }
    )


class FoldersService(newsroom.Service):
    def __init__(self, datasource: str, backend=None):
        super().__init__(datasource, backend)
        user_deleted.connect(self.on_user_deleted)

    def on_deleted(self, doc):
        self.delete_action({"parent": doc["_id"]})
        topics.topics_service.delete_action({"folder": doc["_id"]})

    def on_user_deleted(self, sender, user, **kwargs):
        self.delete_action({"user": user["_id"]})


class UserFoldersService(FoldersService):
    pass


class CompanyFoldersService(FoldersService):
    pass


folders_service = FoldersService("topic_folders", superdesk.get_backend())
