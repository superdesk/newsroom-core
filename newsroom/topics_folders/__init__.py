from superdesk.core.module import Module
from newsroom.types import Company, User

from .folders import (
    company_topic_folder_resource_config,
    user_topic_folders_resource_config,
    topic_folders_resource_config,
    CompanyFoldersResourceService,
    UserFoldersResourceService,
)


module = Module(
    name="newsroom.topics_folders",
    resources=[company_topic_folder_resource_config, user_topic_folders_resource_config, topic_folders_resource_config],
)


async def get_user_folders(user: User, section: str):
    mongo_cursor = await UserFoldersResourceService().search(
        lookup={
            "user": user["_id"],
            "section": section,
        },
    )
    return await mongo_cursor.to_list_raw()


async def get_company_folders(company: Company, section: str):
    mongo_cursor = await CompanyFoldersResourceService().search(
        lookup={
            "company": company["_id"],
            "section": section,
        },
    )
    return await mongo_cursor.to_list_raw()
