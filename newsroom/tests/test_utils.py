from typing import Any

from io import BytesIO
from bson import ObjectId
from lxml import html as lxml_html

from superdesk import get_resource_service
from superdesk.utc import utcnow

from newsroom.types import EmbedPermissionUserAction
from newsroom.core import get_current_wsgi_app


async def find_one_by_id(resource: str, item_id: ObjectId | str) -> Any | None:
    """
    Attempts to create a new resource entries. First tries with async, otherwise it falls back to
    sync resources.
    """
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        model_instance = await async_app.resources.get_resource_service(resource).find_by_id(item_id)
        return model_instance.to_dict(context={"use_objectid": True}) if model_instance else None
    except KeyError:
        return app.data.find_one(resource, req=None, _id=item_id)


async def find_one_for(resource: str, **kwargs: Any) -> Any | None:
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        model_instance = await async_app.resources.get_resource_service(resource).find_one(**kwargs)
        return model_instance.to_dict(context={"use_objectid": True}) if model_instance else None
    except KeyError:
        return app.data.find_one(resource, req=None, **kwargs)


async def get_all(resource: str) -> list[Any]:
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        return [item async for item in async_app.resources.get_resource_service(resource).get_all_raw()]
    except KeyError:
        return [item for item in app.data.find(resource, {})]


async def add_company_products(app, company_id, products):
    company = await find_one_by_id("companies", company_id)
    await create_entries_for("products", products)
    company_products = company["products"] or []

    for product in products:
        company_products.append({"_id": product["_id"], "section": product["product_type"], "seats": 0})

    await update_entries_for("companies", company["_id"], {"products": company_products}, company)


async def create_entries_for(resource: str, items: list[Any]) -> list[ObjectId | str]:
    """
    Attempts to create a new resource entries. First tries with async, otherwise it falls back to
    sync resources.
    """
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        items = await async_app.resources.get_resource_service(resource).create(items)
        return [item.id for item in items]
    except KeyError:
        print(f"Failed to find async service for {resource}")
        ids = []
        for item in items:
            app.data.mongo._mongotize(item, resource)
            ids.extend(get_resource_service(resource).post([item]))
        return ids


async def update_entries_for(
    resource: str, item_id: str | ObjectId, updates: dict[str, Any], original: Any | None = None
):
    """
    Attempts to update existing resource entries. First tries with async, otherwise it falls back to
    sync resources.
    """
    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        await async_app.resources.get_resource_service(resource).update(item_id, updates)
    except KeyError:
        app.data.update(resource, item_id, updates, original)


async def delete_entries_for(resource: str) -> None:
    """
    Attempts to remove all items from the resources MongoDB and/or Elastic.
    First tries with async, otherwise it falls back to sync resources.
    """

    app = get_current_wsgi_app()
    async_app = app.async_app

    try:
        await async_app.resources.get_resource_service(resource).delete_many({})
    except KeyError:
        app.data.remove(resource)


def get_download_filename(filename: str, item: dict) -> str:
    return "%s-%s" % (item["versioncreated"].strftime("%Y%m%d%H%M"), filename)


async def download_zip_file(client, items_ids, _format, section):
    now = utcnow()
    payload = {"items": items_ids, "type": section, "format": _format}
    resp = await client.post("/download", json=payload)
    assert resp.status_code == 200, await resp.get_data(as_text=True)
    assert resp.mimetype == "application/zip"
    assert resp.headers.get("Content-Disposition") == "attachment; filename={}-newsroom.zip".format(
        now.strftime("%Y%m%d%H%M")
    )
    _file = BytesIO(await resp.get_data())
    return _file


def test_embed_permissions(item: dict, tests: dict[str, list[EmbedPermissionUserAction]]) -> None:
    from newsroom.wire.embeds import iterate_embeds

    html = lxml_html.fromstring(item.get("body_html") or "")
    embed_ids: list[str] = []
    for comment, editor_id in iterate_embeds(html):
        embed_ids.append(editor_id)
        test = tests.get(editor_id)

        if not test:
            continue

        assert EmbedPermissionUserAction.DISPLAY in test
        association = (item.get("associations") or {}).get(editor_id)
        assert association is not None
        content_type = association.get("type")

        if content_type in {"audio", "video"}:
            if content_type == "video":
                media_element = comment.getnext().find("./video")
            else:
                media_element = comment.getnext().find("./audio")

            assert media_element is not None
            if EmbedPermissionUserAction.DOWNLOAD in test:
                assert media_element.attrib.get("data-disable-download") != "true"
            else:
                assert media_element.attrib.get("data-disable-download") == "true"

    # Test embeds that should be shown/not shown
    for embed_id, test in tests.items():
        if EmbedPermissionUserAction.DISPLAY in test:
            assert embed_id in embed_ids
            assert (item.get("associations") or {}).get(embed_id)
        else:
            assert embed_id not in embed_ids
            assert not (item.get("associations") or {}).get(embed_id)
