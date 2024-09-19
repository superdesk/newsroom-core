import bson
from tests.core.utils import create_entries_for
from newsroom.topics_folders.folders import FolderResourceService
from newsroom.topics.topics_async import TopicService
from newsroom.users.service import UsersService

# TODO-ASYNC: update these Tests when conversion of Signals is completed


async def test_data_update(app):
    users = [
        {
            "_id": bson.ObjectId("66ec5269ff878dbc1fc4fe48"),
            "first_name": "3Foo",
            "last_name": "Bar",
            "email": "bar@example.com",
        },
        {
            "_id": bson.ObjectId("66ec5288a73384b520ade434"),
            "first_name": "Foo",
            "last_name": "Bar",
            "email": "foo@example.com",
        },
    ]
    await create_entries_for("users", users)

    await create_entries_for(
        "user_topic_folders",
        [
            {"_id": bson.ObjectId(), "name": "foo", "user": users[0]["_id"], "section": "wire"},
            {"_id": bson.ObjectId(), "name": "baz", "user": users[1]["_id"], "section": "wire"},
        ],
    )

    await create_entries_for(
        "topics",
        [
            {"_id": bson.ObjectId(), "label": "topic1", "user": users[0]["_id"], "topic_type": "wire"},
            {
                "_id": bson.ObjectId(),
                "label": "topic2",
                "is_global": False,
                "user": users[1]["_id"],
                "topic_type": "wire",
            },
            {
                "_id": bson.ObjectId(),
                "label": "topic3",
                "is_global": True,
                "user": users[0]["_id"],
                "topic_type": "wire",
                "subscribers": [
                    {"user_id": users[0]["_id"]},
                    {"user_id": users[1]["_id"]},
                ],
            },
        ],
    )

    await UsersService().delete_many(lookup={"_id": bson.ObjectId("66ec5269ff878dbc1fc4fe48")})

    user_ids = [user["_id"] for user in users]
    # Remove missing user private topics
    print("DELETE PRIVATE TOPICS")
    await TopicService().delete_many(lookup={"user": {"$nin": user_ids}, "is_global": False})

    # Remove missing subscribers
    print("REMOVE MISSING SUBSCRIBERS")
    missing_subscribers = {"subscribers": {"$elemMatch": {"user_id": {"$nin": user_ids}}}}
    await TopicService().update_many(missing_subscribers, {"$pull": {"subscribers": {"user_id": {"$nin": user_ids}}}})

    # Unset missing users from global folders
    print("UNSET USER ON GLOBAL TOPICS")
    await TopicService().update_many({"user": {"$nin": user_ids}}, {"user": None})

    # Delete missing user folders
    print("DELETE USER FOLDERS")
    await FolderResourceService().delete_many({"user": {"$nin": user_ids, "$exists": True}})

    cursor = await FolderResourceService().search(lookup={})
    folders = await cursor.to_list_raw()
    assert 2 == len(folders)
    assert "foo" == folders[0]["name"]

    cursor = await TopicService().search(lookup={})
    topics = await cursor.to_list_raw()
    assert 3 == len(topics)
    assert "topic1" == topics[0]["label"]
    assert "topic2" == topics[1]["label"]
    assert 1 == len(topics[2]["subscribers"])
    assert users[1]["_id"] == topics[2]["subscribers"][0]["user_id"]
