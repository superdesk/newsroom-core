from unittest.mock import patch
from redis.exceptions import ConnectionError as RedisConnectionError
from newsroom.factory.cache import NewshubCache


def redis_down(*args, **kwargs):
    raise RedisConnectionError("Error while reading from redis:6379 : (104, 'Connection reset by peer')")


async def test_company_and_user_are_created_when_redis_cache_fails(app, auth_headers):
    """Cache errors must not fail the request"""
    client = app.test_client()

    with (
        patch.object(NewshubCache, "set", side_effect=redis_down),
        patch.object(NewshubCache, "set_many", side_effect=redis_down),
        patch.object(NewshubCache, "delete", side_effect=redis_down),
    ):
        async with app.test_app():
            response = await client.post("/api/companies", json={"name": "Test Company"}, headers=auth_headers)
            assert response.status_code == 201, await response.get_json()
            company = await response.get_json()
            company_id = company["_id"]

            response = await client.patch(
                f"/api/companies/{company_id}",
                json={"name": "Test Company Updated"},
                headers={**auth_headers, "If-Match": company["_etag"]},
            )
            assert response.status_code == 200, await response.get_json()

            response = await client.post(
                "/api/users",
                json={
                    "email": "user@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "user_type": "public",
                    "company": company_id,
                },
                headers=auth_headers,
            )
            assert response.status_code == 201, await response.get_json()

    response = await client.get(f"/api/companies/{company_id}", headers=auth_headers)
    assert response.status_code == 200
    assert (await response.get_json())["name"] == "Test Company Updated"

    response = await client.get("/api/users", headers=auth_headers)
    users = (await response.get_json())["_items"]
    assert [user["email"] for user in users] == ["user@example.com"]
    assert users[0]["company"] == company_id
