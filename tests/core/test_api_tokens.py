from quart import json
from bson import ObjectId
import urllib.parse


async def test_api_tokens_create(client):
    response = await client.post(
        "/news_api_tokens",
        json={"company": "5b504318975bd5227e5ea0b9"},
    )
    data = json.loads(await response.get_data())
    assert "token" in data
    assert response.status_code == 201


async def test_api_tokens_create_expired(client):
    response = await client.post(
        "/news_api_tokens",
        json={
            "company": "5b504318975bd5227e5ea0b9",
            "expiry": "1999-08-22T04:23:06+0000",
        }
    )
    data = json.loads(await response.get_data())
    assert "error" in data
    assert response.status_code == 400


async def test_api_tokens_create_only_one_per_company(client):
    response = await client.post(
        "/news_api_tokens",
        json={"company": "5b504318975bd5227e5ea0b9"},
    )
    data = json.loads(await response.get_data())
    assert "token" in data
    assert response.status_code == 201
    response = await client.post(
        "/news_api_tokens",
        json={"company": "5b504318975bd5227e5ea0b9"},
    )
    data = json.loads(await response.get_data())
    assert "error" in data
    assert response.status_code == 400


async def test_api_tokens_patch(client, app):
    data = app.data.insert(
        "news_api_tokens",
        [
            {
                "company": ObjectId("5b504318975bd5227e5ea0b9"),
                "enabled": True,
            }
        ],
    )
    response = await client.patch(
        "/news_api_tokens?token={}".format(urllib.parse.quote(data[0])),
        json={"enabled": False, "expiry": "2023-08-22T04:23:06+0000"},
    )
    data = json.loads(await response.get_data())
    assert data.get("enabled") is False
    assert response.status_code == 200
