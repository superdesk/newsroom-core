from bson import ObjectId
from quart import json
from pytest import fixture


from newsroom.types import CardResourceModel, DashboardCardType
from newsroom.cards import CardsResourceService
from tests.utils import logout


@fixture(autouse=True)
async def init(app):
    await CardsResourceService().create(
        [
            CardResourceModel(
                id=ObjectId("59b4c5c61d41c8d736852fbf"),
                label="Sport",
                dashboard_type=DashboardCardType.TEXT_6,
                dashboard="newsroom",
                config=dict(
                    product="5a23c1131d41c82b8dd4267d",
                    size=6,
                ),
            )
        ]
    )


async def test_card_list_fails_for_anonymous_user(client):
    await logout(client)
    response = await client.get("/cards")
    assert response.status_code == 302


async def test_save_and_return_cards(client):
    # Save a new card
    response = await client.post(
        "/cards/new",
        form=dict(
            card=json.dumps(
                dict(
                    label="Local News",
                    type=DashboardCardType.PIC_TEXT_4,
                    config=dict(
                        product="5a23c1131d41c82b8dd4267d",
                        size=4,
                    ),
                )
            )
        ),
    )
    assert response.status_code == 201, await response.get_data(as_text=True)

    response = await client.get("/cards")
    assert "Local" in await response.get_data(as_text=True)


async def test_update_card(client):
    await client.post(
        "/cards/59b4c5c61d41c8d736852fbf/",
        form={"card": json.dumps({"label": "Sport", "dashboard": "newsroom", "type": "4-picture-text"})},
    )

    response = await client.get("/cards")
    assert "4-picture-text" in await response.get_data(as_text=True)


async def test_delete_card_succeeds(client):
    await client.delete("/cards/59b4c5c61d41c8d736852fbf")

    response = await client.get("/cards")
    data = json.loads(await response.get_data())
    assert 0 == len(data)


async def test_validate_create_card(client):
    card = dict()
    response = await client.post("/cards/new", form=dict(card=json.dumps(card)))
    assert response.status_code == 400
    data = await response.get_json()
    assert "required" in data["label"]
    assert "required" in data["type"]

    card = dict(
        label="    ",
        type=DashboardCardType.PIC_TEXT_4,
    )
    response = await client.post("/cards/new", form=dict(card=json.dumps(card)))
    assert response.status_code == 400
    data = await response.get_json()
    assert "label" in data
    assert "type" not in data

    card = dict(
        label="Local News",
        type="foo_bar_types",
    )
    response = await client.post("/cards/new", form=dict(card=json.dumps(card)))
    assert response.status_code == 400
    data = await response.get_json()
    assert "label" not in data
    assert "type" in data

    card = dict(label="Local News", type=DashboardCardType.PIC_TEXT_4)
    response = await client.post("/cards/new", form=dict(card=json.dumps(card)))
    assert response.status_code == 201


async def test_validate_update_card(client):
    card = dict(label="Local News", type=DashboardCardType.PIC_TEXT_4)
    response = await client.post("/cards/new", form=dict(card=json.dumps(card)))
    assert response.status_code == 201
    card_id = (await response.get_json())["_id"]

    updates = dict(
        label=None,
        type="blah",
    )
    response = await client.post(f"/cards/{card_id}", form=dict(card=json.dumps(updates)))
    assert response.status_code == 400
    data = await response.get_json()
    print(data)
    assert "label" in data
    assert "type" in data

    updates = dict(
        label="Test Name",
        type=DashboardCardType.PIC_TEXT_3,
    )
    response = await client.post(f"/cards/{card_id}", form=dict(card=json.dumps(updates)))
    assert response.status_code == 200
