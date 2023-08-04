import tests.utils as utils


def test_user_sections(app, client, user):
    topics = [{"label": "test"}]
    app.data.insert("topics", topics)

    utils.patch_json(
        client,
        f"/api/_users/{user['_id']}",
        {
            "dashboards": [{"name": "test", "type": "test", "topic_ids": [t["_id"] for t in topics]}],
        },
    )

    data = utils.get_json(
        client,
        f"/api/_users/{user['_id']}",
    )

    assert "dashboards" in data
