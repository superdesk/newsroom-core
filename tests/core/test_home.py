from flask import session as server_session

from newsroom.wire.views import get_home_data
from newsroom.tests.fixtures import PUBLIC_USER_ID


def test_personal_dashboard_data(client, app, company_products):
    with app.test_request_context():
        server_session["user"] = str(PUBLIC_USER_ID)
        server_session["user_type"] = "public"

        user = app.data.find_one("users", req=None, _id=PUBLIC_USER_ID)
        assert user

        topics = [
            {"name": "label", "query": "weather", "user": PUBLIC_USER_ID, "topic_type": "wire"},
        ]

        app.data.insert("topics", topics)

        app.data.update(
            "users",
            PUBLIC_USER_ID,
            {
                "dashboards": [
                    {"name": "test d", "type": "4x4", "topic_ids": [topic["_id"] for topic in topics]},
                ]
            },
            user,
        )

        data = get_home_data()

    assert "personalizedDashboards" in data
    dashboard_data = data["personalizedDashboards"][0]
    assert dashboard_data["dashboard_name"] == "test d"
    assert dashboard_data["dashboard_id"] == "d0"
    topic_items = dashboard_data["topic_items"]
    assert 1 == len(topic_items)
    assert topic_items[0]["_id"] == topics[0]["_id"]
    assert 1 == len(topic_items[0]["items"])
    assert "Weather" == topic_items[0]["items"][0]["headline"]
