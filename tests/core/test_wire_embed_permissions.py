from bson import ObjectId

from newsroom.tests import test_utils
from tests.utils import login

from ..fixtures import (
    items,
    PUBLIC_USER_EMAIL,
    COMPANY_1_ID,
)


async def setup_embeds():
    media_id = str(ObjectId())
    item = items[:2][0]
    associations = {
        "editor_1": {
            "type": "video",
            "renditions": {
                "original": {
                    "mimetype": "video/mp4",
                    "href": "/assets/640ff0bdfb5122dcf06a6fc3",
                    "media": media_id,
                }
            },
            "mimetype": "video/mp4",
            "products": [{"code": "123", "name": "Product A"}, {"code": "321", "name": "Product B"}],
        },
        "editor_0": {
            "type": "audio",
            "renditions": {
                "original": {
                    "mimetype": "audio/mp3",
                    "href": "/assets/640feb9bfb5122dcf06a6f7c",
                    "media": "640feb9bfb5122dcf06a6f7c",
                }
            },
            "mimetype": "audio/mp3",
            "products": [{"code": "999", "name": "NSW News"}],
        },
        "editor_3": None,
    }

    await test_utils.update_entries_for(
        "items",
        item["_id"],
        {
            "associations": associations,
            "body_html": '<p>Par 1</p><!-- EMBED START Audio {id: "editor_0"} --><figure>'
            '<audio controls src="/assets/640feb9bfb5122dcf06a6f7c" alt="minns" '
            'width="100%" height="100%"></audio>'
            "<figcaption>minns</figcaption>"
            "</figure>"
            '<!-- EMBED END Audio {id: "editor_0"} -->'
            "<p><br></p>"
            "<p>Par 2</p>"
            '<!-- EMBED START Video {id: "editor_1"} -->'
            "<figure>"
            '<video controls src="/assets/640ff0bdfb5122dcf06a6fc3" '
            'alt="Scomo text" width="100%" height="100%">'
            "</video>"
            "<figcaption>Scomo whinging</figcaption>"
            "</figure>"
            '<!-- EMBED END Video {id: "editor_1"} -->'
            "<p><br></p>Par 3<p></p>"
            "<p>Par 4</p>",
        },
        item,
    )


async def test_embed_permissions_for_admins(client, app):
    app.config["WIRE_EMBED_PERMISSIONS"] = True
    await test_utils.update_entries_for(
        "companies",
        COMPANY_1_ID,
        {
            "embed_permissions": {"video": ["display"], "audio": ["display"], "sd_product": ["display"]},
        },
    )
    await test_utils.add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "Service A",
                "is_enabled": True,
                "query": "service.code: a",
                "product_type": "wire",
            },
            {
                "name": "product test",
                "is_enabled": True,
                "sd_product_id": "123",
                "product_type": "wire",
            },
        ],
    )
    await setup_embeds()
    resp = await client.get("/wire/search?type=wire")
    data = await resp.get_json()

    test_utils.test_embed_permissions(
        data["_items"][0],
        {
            "editor_0": ["display", "download"],
            "editor_1": ["display", "download"],
        },
    )


async def test_embed_mark_disable_download(client, app):
    app.config["WIRE_EMBED_PERMISSIONS"] = True
    await login(client, {"email": PUBLIC_USER_EMAIL})
    await test_utils.update_entries_for(
        "companies",
        COMPANY_1_ID,
        {
            "embed_permissions": {"video": ["display"], "audio": ["display"], "sd_product": ["display"]},
        },
    )
    await test_utils.add_company_products(
        app,
        COMPANY_1_ID,
        [
            {
                "name": "Service A",
                "is_enabled": True,
                "query": "service.code: a",
                "product_type": "wire",
            },
            {
                "name": "product test",
                "is_enabled": True,
                "sd_product_id": "123",
                "product_type": "wire",
            },
        ],
    )
    await setup_embeds()
    resp = await client.get("/wire/search?type=wire")

    data = await resp.get_json()

    test_utils.test_embed_permissions(
        data["_items"][0],
        {
            "editor_0": [],
            "editor_1": ["display"],
        },
    )
