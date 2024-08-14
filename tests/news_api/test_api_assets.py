import os
from superdesk.storage.desk_media_storage import SuperdeskGridFSMediaStorage
from tests.news_api.test_api_audit import audit_check


def get_fixture_path(fixture):
    return os.path.join(os.path.dirname(__file__), "../fixtures", fixture)


def setup_image(app):
    with open(get_fixture_path("picture.jpg"), "rb") as f:
        return SuperdeskGridFSMediaStorage(app=app).put(f, "picture.jpg", content_type="image/jpg")


async def test_get_asset(client, app):
    app.data.insert(
        "companies",
        [{"_id": "company_123", "name": "Test Company", "is_enabled": True}],
    )
    app.data.insert("news_api_tokens", [{"company": "company_123", "enabled": True}])
    token = app.data.find_one("news_api_tokens", req=None, company="company_123")

    image_id = setup_image(app)
    response = await client.get("api/v1/assets/{}".format(image_id), headers={"Authorization": token.get("token")})
    assert response.status_code == 200
    audit_check(str(image_id))


async def test_authorization_get_asset(client, app):
    response = await client.get("api/v1/assets/{}".format(id), headers={"Authorization": "xxxxxxxx"})
    assert response.status_code == 401
