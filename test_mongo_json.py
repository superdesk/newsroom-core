from UserModel import UserResourceModel, Dashboard
from bson import ObjectId
from pprint import pprint

# from superdesk.core.resources.utils import convert_json_for_mongo_storage

user = UserResourceModel(
    id=ObjectId(),
    first_name="Mark",
    last_name="Pittaway",
    email="mark.pittaway@sourcefabric.org",
    company=ObjectId(),
    dashboards=[
        Dashboard(
            name="mine",
            type="wire",
            topic_ids=[ObjectId()],
        ),
    ],
    ids=[ObjectId(), ObjectId()],
)
# pprint(user.model_dump(by_alias=True, exclude_unset=True))
pprint(user.model_dump(by_alias=True, exclude_unset=True, context={"for_mongodb": True}, include={"id", "dashboards"}))
