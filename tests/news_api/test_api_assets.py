import os
from bson import ObjectId
from tests.news_api.test_api_audit import audit_check
from tests.core.utils import create_entries_for, find_one_for


def get_fixture_path(fixture):
    return os.path.join(os.path.dirname(__file__), "../fixtures", fixture)


async def setup_image(app):
    with open(get_fixture_path("picture.jpg"), "rb") as f:
        return await app.media.put_async(
            f,
            content_type="image/jpg",
            filename="picture.jpg",
        )


async def test_get_asset(client, app):
    company_id = ObjectId()
    await create_entries_for(
        "companies",
        [{"_id": company_id, "name": "Test Company", "is_enabled": True}],
    )
    await create_entries_for("news_api_tokens", [{"company": company_id, "enabled": True}])
    token = await find_one_for("news_api_tokens", company=company_id)

    image_id = await setup_image(app)
    response = await client.get("api/v1/assets/{}".format(image_id), headers={"Authorization": token.get("token")})
    assert response.status_code == 200
    await audit_check(str(image_id))


async def test_authorization_get_asset(client, app):
    response = await client.get("api/v1/assets/{}".format(id), headers={"Authorization": "xxxxxxxx"})
    assert response.status_code == 401
