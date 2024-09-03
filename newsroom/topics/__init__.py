import superdesk
from superdesk.core.module import Module

from . import folders, topics
from .topics_async import topic_resource_config, topic_endpoints, init, get_user_topics  # noqa
from .folders_async import (
    company_topic_folder_resource_config,
    user_topic_folders_resource_config,
)


def init_app(app):
    topics.TopicsResource("topics", app, topics.topics_service)
    folders.FoldersResource("topic_folders", app, folders.folders_service)

    superdesk.register_resource("user_topic_folders", folders.UserFoldersResource, folders.UserFoldersService, _app=app)
    superdesk.register_resource(
        "company_topic_folders", folders.CompanyFoldersResource, folders.CompanyFoldersService, _app=app
    )


module = Module(
    init=init,
    name="newsroom.topics",
    resources=[topic_resource_config, company_topic_folder_resource_config, user_topic_folders_resource_config],
    endpoints=[topic_endpoints],
)

# TODO-ASYNC :- use this when we update Folder resource to async.

# async def get_user_folders(user, section):
#     mongo_cursor = await UserFoldersResourceService().search(
#         lookup={
#             "user": user["_id"],
#             "section": section,
#         },
#     )
#     return await mongo_cursor.to_list_raw()


# async def get_company_folders(company, section):
#     mongo_cursor = await CompanyFoldersResourceService().search(
#         lookup={
#             "company": company["_id"],
#             "section": section,
#         },
#     )
#     return await mongo_cursor.to_list_raw()


async def get_user_folders(user, section):
    return list(
        superdesk.get_resource_service("user_topic_folders").get(
            req=None,
            lookup={
                "user": user["_id"],
                "section": section,
            },
        )
    )


async def get_company_folders(company, section):
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
