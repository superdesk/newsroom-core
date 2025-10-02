from typing import Any
import bson
from datetime import timedelta
from copy import deepcopy

from zipfile import ZipFile
import lxml.html as lxml_html

from superdesk.core import json
from superdesk.utc import utcnow

from newsroom.tests import test_utils
from newsroom.tests.fixtures import (  # noqa
    user,
    auth_users,
    items,
    init_items,
    init_auth,
    ADMIN_USER_ID,
)
from .test_push import upload_binary, get_fixture_path

items_ids = [item["_id"] for item in items[:2]]
item = deepcopy(items[0])

media_id = str(bson.ObjectId())
associations: dict[str, Any] = {
    "featuremedia": {
        "mimetype": "image/jpeg",
        "type": "picture",
        "products": [{"code": "123", "name": "Product A"}],
        "renditions": {
            "16-9": {
                "mimetype": "image/jpeg",
                "href": "http://a.b.c/xxx.jpg",
                "media": media_id,
                "width": 1280,
                "height": 720,
            },
            "4-3": {
                "href": "/assets/633d11b9fb5122dcf06a6f02",
                "width": 800,
                "height": 600,
                "media": media_id,
                "mimetype": "image/jpeg",
            },
        },
    },
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
        "products": [
            {"code": "123", "name": "Product A"},
            {"code": "321", "name": "Product B"},
        ],
    },
    "editor_0": {
        "type": "audio",
        "renditions": {
            "original": {
                "mimetype": "audio/mp3",
                "href": "/assets/640feb9bfb5122dcf06a6f7c",
                "media": media_id,
            }
        },
        "mimetype": "audio/mp3",
        "products": [{"code": "999", "name": "NSW News"}],
    },
    "editor_2": {
        "type": "picture",
        "renditions": {
            "4-3": {
                "href": "/assets/633d11b9fb5122dcf06a6f03",
                "width": 800,
                "height": 600,
                "mimetype": "image/jpeg",
                "media": media_id,
            },
            "16-9": {
                "href": "/assets/633d0f59fb5122dcf06a6ee8",
                "width": 1280,
                "height": 720,
                "mimetype": "image/jpeg",
                "media": media_id,
                "poi": {},
            },
        },
        "products": [{"code": "888"}],
    },
    "editor_3": None,
}


async def _setup_embeds(client):
    await upload_binary("picture.jpg", client, media_id=media_id)

    await test_utils.update_entries_for(
        "items",
        item["_id"],
        {
            "associations": deepcopy(associations),
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
            '<!-- EMBED START Image {id: "editor_2"} -->'
            "<figure>"
            '<img src="/assets/6189e8a48b37621081610714_newsroom_custom" '
            'alt="SCOTT MORRISON MELBOURNE VISIT"'
            ' id="editor_2">'
            "<figcaption>Prime Minister Scott Morrison and Liberal member for "
            "Higgins Katie Allen</figcaption>"
            "</figure>"
            '<!-- EMBED END Image {id: "editor_2"} -->'
            "<p>Par 4</p>",
        },
        item,
    )


async def _setup_company_user_products(client, app) -> bson.ObjectId:
    await _setup_embeds(client)
    app.config["WIRE_EMBED_PERMISSIONS"] = True
    company_id = bson.ObjectId()
    await test_utils.create_entries_for(
        "companies",
        [
            {
                "_id": company_id,
                "name": "Another Press co.",
                "is_enabled": True,
                "embed_permissions": {
                    "picture": ["display"],
                    "video": ["display", "download"],
                    "audio": ["display", "download"],
                    "sd_product": ["display"],
                },
            }
        ],
    )
    admin_user = await test_utils.find_one_for("users", req=None, first_name="admin")
    assert admin_user
    await test_utils.update_entries_for(
        "users",
        admin_user["_id"],
        {"company": company_id, "user_type": "public"},
        admin_user,
    )
    await test_utils.create_entries_for(
        "products",
        [
            {
                "name": "product test",
                "sd_product_id": "123",
                "companies": [company_id],
                "is_enabled": True,
                "product_type": "wire",
            }
        ],
    )
    app.general_setting("news_api_allowed_renditions", "Foo", default="16-9,4-3")
    return company_id


def _assert_ninjs_content(content: str, item: dict, media_included: list[str]) -> dict:
    data = json.loads(content)
    assert item["slugline"] == data["slugline"]
    assert item["headline"] == data["headline"]

    for media_id in ("editor_0", "editor_1", "editor_2"):
        if media_id in media_included:
            assert data.get("associations").get(media_id)
        else:
            assert not data.get("associations").get(media_id)

    return data


def _assert_html_content(content: str, item: dict, use_base64: bool = False) -> None:
    root = lxml_html.fromstring(content)

    if use_base64:
        with open(get_fixture_path("picture.jpg"), "rb") as original_fixture:
            from base64 import b64encode

            fixture_data = b64encode(original_fixture.read()).decode("utf-8")
            featuremedia_src = "data:image/jpeg;base64," + fixture_data
            video_src = "data:video/mp4;base64," + fixture_data
    else:
        featuremedia_src = _get_rendition_href("featuremedia", "16-9")
        video_src = _get_rendition_href("editor_1", "original")

    if root.tag == "html":
        assert root.find("head/title").text == f"Newshub : {item['headline']}"
        assert root.find("body//article/pre").text == item["slugline"]
        assert root.find("body//article/h1").text == item["headline"]
        footer_text = root.find("body/footer").text_content()
        assert "All contents © Copyright 2025 Sourcefabric. All rights reserved." in footer_text

        featuremedia_element = root.xpath("//img[@id='feature-image']")[0]
        assert featuremedia_element.attrib["src"] == featuremedia_src

    assert "editor_0" not in content
    assert "editor_2" not in content
    video_element = root.xpath("//video[@id='editor_1']")[0]
    assert video_element.attrib["src"] == video_src


def _assert_html_content_without_embeds(content: str, item: dict) -> None:
    root = lxml_html.fromstring(content)

    if root.tag == "html":
        assert root.tag == "html"
        assert root.find("head/title").text == item["headline"]
        assert root.find("body//p").text == item["slugline"]
        assert root.find("body//h1").text == item["headline"]

    assert len(root.xpath("//img")) == 0
    assert len(root.xpath("//video")) == 0
    assert len(root.xpath("//audio")) == 0


def _get_rendition_href(association: str, rendition: str) -> str:
    href = associations[association]["renditions"][rendition]["href"]
    return href[1:] if href.startswith("/") else href


def _assert_zip_file_contents(zf: ZipFile, expected_files: dict[str, bytes | None]) -> None:
    assert sorted(zf.namelist()) == sorted(expected_files.keys())
    for filename, expected_data in expected_files.items():
        if expected_data is None:
            continue
        assert zf.open(filename).read() == expected_data


async def _assert_download_history_entries(
    company_id: bson.ObjectId, expected_item_actions: dict[str, list[str]]
) -> None:
    history_items = await test_utils.get_all("history")
    assert len(history_items) == sum(len(actions) for actions in expected_item_actions.values())

    item_actions: dict[str, list[str]] = {}
    for history_item in history_items:
        item_actions.setdefault(history_item["item"], []).append(history_item["action"])

    assert sorted(item_actions.keys()) == sorted(expected_item_actions.keys())
    for item_id, expected_actions in expected_item_actions.items():
        assert sorted(item_actions[item_id]) == sorted(expected_actions)

    for history_entry in history_items:
        assert history_entry.get("item") in items_ids
        assert history_entry.get("user") == bson.ObjectId(ADMIN_USER_ID)
        assert history_entry.get("versioncreated") + timedelta(seconds=2) >= utcnow()
        assert history_entry.get("version")
        assert history_entry.get("company") == company_id
        assert history_entry.get("section") == "wire"


async def _download_file(client, item_id: str, download_format: str):
    response = await client.post("/download", json={"items": [item_id], "type": "wire", "format": download_format})
    assert response.status_code == 200, await response.get_data(as_text=True)
    return await response.get_data()


async def test_html_download(client, app):
    """Tests HTMLFormatter"""
    company_id = await _setup_company_user_products(client, app)
    html_file = await _download_file(client, items_ids[0], "html")
    _assert_html_content_without_embeds(html_file, items[0])
    await _assert_download_history_entries(company_id, {items[0]["_id"]: ["download"]})


async def test_html_media_formatter_download(client, app):
    """Tests HTMLMediaFormatter"""

    company_id = await _setup_company_user_products(client, app)
    html_file = await _download_file(client, items_ids[0], "html_media")
    _assert_html_content(html_file.decode("utf-8"), item, use_base64=True)
    await _assert_download_history_entries(
        company_id, {items[0]["_id"]: ["download", "download video", "download picture"]}
    )


async def test_html_package_formatter_download(client, app):
    """Test HTMLPackageFormatter"""

    company_id = await _setup_company_user_products(client, app)
    _file = await test_utils.download_zip_file(client, [items[0]["_id"]], "html_package", "wire")

    with ZipFile(_file) as zf, open(get_fixture_path("picture.jpg"), "rb") as original_fixture:
        original_fixture_data = original_fixture.read()
        content_filename = test_utils.get_download_filename("amazon-bookstore-opening.html", item)

        _assert_zip_file_contents(
            zf,
            {
                content_filename: None,
                _get_rendition_href("featuremedia", "16-9"): original_fixture_data,
                _get_rendition_href("featuremedia", "4-3"): original_fixture_data,
                _get_rendition_href("editor_1", "original"): original_fixture_data,
            },
        )
        content = zf.open(content_filename).read()

    _assert_html_content(content.decode("utf-8"), item)
    await _assert_download_history_entries(
        company_id,
        {
            items[0]["_id"]: ["download", "download video", "download picture"],
        },
    )


async def test_ninjs_without_embeds_formatter_download(client, app):
    """Test NINJSWithoutEmbedsFormatter"""

    company_id = await _setup_company_user_products(client, app)
    content = await _download_file(client, items_ids[0], "ninjs_exclude_embeds")
    data = _assert_ninjs_content(content.decode("utf-8"), items[0], [])
    _assert_html_content_without_embeds(data.get("body_html"), item)
    await _assert_download_history_entries(company_id, {items[0]["_id"]: ["download"]})


async def test_ninjs_package_formatter_download(client, app):
    """Test NINJSPackageFormatter"""

    company_id = await _setup_company_user_products(client, app)
    _file = await test_utils.download_zip_file(client, [items[0]["_id"]], "ninjspackage", "wire")

    with ZipFile(_file) as zf:
        content_filename = test_utils.get_download_filename("amazon-bookstore-opening.json", item)
        assert sorted(zf.namelist()) == sorted(
            [
                content_filename,
                _get_rendition_href("featuremedia", "16-9"),
                _get_rendition_href("featuremedia", "4-3"),
                _get_rendition_href("editor_1", "original"),
            ]
        )
        content = zf.open(content_filename).read()

    data = _assert_ninjs_content(content.decode("utf-8"), items[0], ["editor_1"])
    _assert_html_content(data.get("body_html"), item)
    await _assert_download_history_entries(
        company_id,
        {
            items[0]["_id"]: ["download", "download video", "download picture"],
        },
    )


async def test_ninjs_package_formatter_download_multiple(client, app):
    """Test NINJSPackageFormatter"""

    company_id = await _setup_company_user_products(client, app)
    _file = await test_utils.download_zip_file(client, items_ids, "ninjspackage", "wire")

    with ZipFile(_file) as zf:
        content_filename = test_utils.get_download_filename("amazon-bookstore-opening.json", item)
        assert sorted(zf.namelist()) == sorted(
            [
                test_utils.get_download_filename("weather.json", items[1]),
                content_filename,
                _get_rendition_href("featuremedia", "16-9"),
                _get_rendition_href("featuremedia", "4-3"),
                _get_rendition_href("editor_1", "original"),
            ]
        )
        content = zf.open(content_filename).read()

    data = _assert_ninjs_content(content.decode("utf-8"), items[0], ["editor_1"])
    _assert_html_content(data.get("body_html"), item)
    await _assert_download_history_entries(
        company_id,
        {
            items[0]["_id"]: ["download", "download video", "download picture"],
            items[1]["_id"]: ["download"],
        },
    )


async def test_html_package_formatter_download_multiple(client, app):
    """Test HTMLPackageFormatter"""
    company_id = await _setup_company_user_products(client, app)
    _file = await test_utils.download_zip_file(client, items_ids, "html_package", "wire")

    with ZipFile(_file) as zf, open(get_fixture_path("picture.jpg"), "rb") as original_fixture:
        original_fixture_data = original_fixture.read()
        content_filename = test_utils.get_download_filename("amazon-bookstore-opening.html", item)

        _assert_zip_file_contents(
            zf,
            {
                test_utils.get_download_filename("weather.html", items[1]): None,
                content_filename: None,
                _get_rendition_href("featuremedia", "16-9"): original_fixture_data,
                _get_rendition_href("featuremedia", "4-3"): original_fixture_data,
                _get_rendition_href("editor_1", "original"): original_fixture_data,
            },
        )
        content = zf.open(content_filename).read()

    _assert_html_content(content.decode("utf-8"), item)
    await _assert_download_history_entries(
        company_id,
        {
            items[0]["_id"]: ["download", "download video", "download picture"],
            items[1]["_id"]: ["download"],
        },
    )


async def test_package_download_permissions(client, app):
    company_id = await _setup_company_user_products(client, app)

    # Remove sdesk product checking, use content type directly and remove download permission for video
    await test_utils.update_entries_for(
        "companies",
        company_id,
        {
            "embed_permissions": {
                "featuremedia": [],
                "picture": [],
                "video": ["display"],
                "audio": ["display", "download"],
            }
        },
    )

    with open(get_fixture_path("picture.jpg"), "rb") as original_fixture:
        original_fixture_data = original_fixture.read()

    _file = await test_utils.download_zip_file(client, items_ids, "html_package", "wire")
    with ZipFile(_file) as zf:
        # pictures and video will not be included, only audio will be
        _assert_zip_file_contents(
            zf,
            {
                test_utils.get_download_filename("weather.html", items[1]): None,
                test_utils.get_download_filename("amazon-bookstore-opening.html", item): None,
                _get_rendition_href("editor_0", "original"): original_fixture_data,
            },
        )
