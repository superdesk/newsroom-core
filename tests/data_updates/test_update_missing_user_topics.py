# TODO-Async, need to check Migrations commands is not working with async resources

# import bson
# import importlib
# from tests.core.utils import create_entries_for
# from newsroom.topics_folders.folders import FolderResourceService
# from newsroom.topics.topics_async import TopicService
# update_module = importlib.import_module("data_updates.00014_20240312-085705_topics")


# async def test_data_update(app):
#     users = [
#         {"name": "foo", "email": "foo"},
#         {"name": "bar", "email": "bar"},
#     ]
#     app.data.insert("users", users)

#     create_entries_for(
#         "topic_folders",
#         [
#             {"_id":bson.ObjectId(),"name": "foo", "user": users[0]["_id"]},
#             {"_id":bson.ObjectId(), "name": "baz", "user": bson.ObjectId()},
#         ],
#     )

#     create_entries_for(
#         "topics",
#         [
#             {"_id":bson.ObjectId(),"label": "topic1", "user": users[0]["_id"]},
#             {"_id":bson.ObjectId(),"label": "topic2", "is_global": False, "user": bson.ObjectId()},
#             {   "_id":bson.ObjectId(),
#                 "label": "topic3",
#                 "is_global": True,
#                 "user": bson.ObjectId(),
#                 "subscribers": [
#                     {"user_id": users[0]["_id"]},
#                     {"user_id": users[1]["_id"]},
#                     {"user_id": bson.ObjectId()},
#                     {"user_id": bson.ObjectId()},
#                 ],
#             },
#         ],
#     )

#     update_module.DataUpdate().apply("forwards")

#     cursor = await FolderResourceService().search(lookup={})
#     folders = await cursor.to_list_raw()
#     assert 1 == len(folders)
#     assert "foo" == folders[0]["name"]

#     cursor = await TopicService().search(lookup={})
#     topics = await cursor.to_list_raw()
#     assert 2 == len(topics)
#     assert "topic1" == topics[0]["label"]
#     assert "topic3" == topics[1]["label"]
#     assert 2 == len(topics[1]["subscribers"])
#     assert users[0]["_id"] == topics[1]["subscribers"][0]["user_id"]
