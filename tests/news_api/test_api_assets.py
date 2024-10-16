import os
from bson import ObjectId
from tests.news_api.test_api_audit import audit_check


def get_fixture_path(fixture):
    return os.path.join(os.path.dirname(__file__), "../fixtures", fixture)


async def setup_image(app):
    with open(get_fixture_path("picture.jpg"), "rb") as f:
        return await app.media_async.put(
            f,
            content_type="image/jpg",
            filename="picture.jpg",
        )


async def test_get_asset(client, app):
    company_id = ObjectId()
    app.data.insert(
        "companies",
        [{"_id": company_id, "name": "Test Company", "is_enabled": True}],
    )
    app.data.insert("news_api_tokens", [{"company": company_id, "enabled": True}])
    token = app.data.find_one("news_api_tokens", req=None, company=company_id)

    image_id = await setup_image(app)
    response = await client.get("api/v1/assets/{}".format(image_id), headers={"Authorization": token.get("token")})
    assert response.status_code == 200
    audit_check(str(image_id))


async def test_authorization_get_asset(client, app):
    response = await client.get("api/v1/assets/{}".format(id), headers={"Authorization": "xxxxxxxx"})
    assert response.status_code == 401
