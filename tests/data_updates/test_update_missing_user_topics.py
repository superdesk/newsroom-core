import bson
import importlib

update_module = importlib.import_module("data_updates.00014_20240312-085705_topics")


def test_data_update(app):
    users = [
        {"name": "foo", "email": "foo"},
        {"name": "bar", "email": "bar"},
    ]
    app.data.insert("users", users)

    app.data.insert(
        "topic_folders",
        [
            {"name": "foo", "user": users[0]["_id"]},
            {"name": "baz", "user": bson.ObjectId()},
        ],
    )

    app.data.insert(
        "topics",
        [
            {"label": "topic1", "user": users[0]["_id"]},
            {"label": "topic2", "is_global": False, "user": bson.ObjectId()},
            {
                "label": "topic3",
                "is_global": True,
                "user": bson.ObjectId(),
                "subscribers": [
                    {"user_id": users[0]["_id"]},
                    {"user_id": users[1]["_id"]},
                    {"user_id": bson.ObjectId()},
                    {"user_id": bson.ObjectId()},
                ],
            },
        ],
    )

    update_module.DataUpdate().apply("forwards")

    folders, count = app.data.find("topic_folders", req=None, lookup={})
    assert 1 == count
    assert "foo" == folders[0]["name"]

    topics, count = app.data.find("topics", req=None, lookup={})
    assert 2 == count
    assert "topic1" == topics[0]["label"]
    assert "topic3" == topics[1]["label"]
    assert 2 == len(topics[1]["subscribers"])
    assert users[0]["_id"] == topics[1]["subscribers"][0]["user_id"]
