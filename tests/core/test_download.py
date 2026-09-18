import io
import json

import bson
import lxml
import zipfile
import icalendar

from datetime import timedelta
from superdesk.utc import utcnow

from ..fixtures import (  # noqa: F401
    items,
    item_ids,
    init_items,
    init_auth,
    agenda_items,
    init_agenda_items,
)
from .test_push import upload_binary
from newsroom.history_async import HistoryService
from newsroom.tests import test_utils

item = items[:2][0]


def text_content_test(content):
    content = content.decode("utf-8").split("\n")
    assert "AMAZON-BOOKSTORE-OPENING" in content[0]
    assert "Amazon Is Opening More Bookstores" in content[1]
    assert "<p>" not in content
    assert "Next line" == content[-1]


def nitf_content_test(content):
    tree = lxml.etree.parse(io.BytesIO(content))
    root = tree.getroot()
    assert "nitf" == root.tag
    head = root.find("head")
    assert items[0]["headline"] == head.find("title").text


def newsmlg2_content_test(content):
    tree = lxml.etree.parse(io.BytesIO(content))
    root = tree.getroot()
    assert "newsMessage" in root.tag


def text_agenda_content_test(content):
    content = content.decode("utf-8").split("\n")
    assert "Conference Planning" in content[0]
    assert "Slugline: Prime Conference" in content[1]
    assert "<p>" not in content


def json_agenda_content_test(content):
    data = json.loads(content.decode("utf-8"))
    assert data["name"] == "Conference Planning"
    assert data["slugline"] == "Prime Conference"


def ical_agenda_content_test(content):
    cal = icalendar.cal.Calendar.from_ical(content)
    assert cal


wire_formats = [
    {
        "format": "text",
        "mimetype": "text/plain",
        "filename": test_utils.get_download_filename("amazon-bookstore-opening.txt", item),
        "test_content": text_content_test,
    },
    {
        "format": "nitf",
        "mimetype": "application/xml",
        "filename": test_utils.get_download_filename("amazon-bookstore-opening.xml", item),
        "test_content": nitf_content_test,
    },
    {
        "format": "newsmlg2",
        "mimetype": "application/vnd.iptc.g2.newsitem+xml",
        "filename": test_utils.get_download_filename("amazon-bookstore-opening.xml", item),
        "test_content": newsmlg2_content_test,
    },
    {"format": "picture", "mimetype": "image/jpeg", "filename": "baseimage.jpg"},
]

agenda_formats = [
    {
        "format": "text",
        "mimetype": "text/plain",
        "filename": "prime-conference.txt",
        "test_content": text_agenda_content_test,
    },
    {
        "format": "json",
        "mimetype": "application/json",
        "filename": "prime-conference.json",
        "test_content": json_agenda_content_test,
    },
    {
        "format": "ical",
        "mimetype": "text/calendar",
        "filename": "prime-conference.ical",
        "test_content": ical_agenda_content_test,
    },
]


async def setup_image(client, app):
    media_id = str(bson.ObjectId())
    await upload_binary("picture.jpg", client, media_id=media_id)
    associations = {
        "featuremedia": {
            "mimetype": "image/jpeg",
            "renditions": {
                "baseImage": {
                    "mimetype": "image/jpeg",
                    "media": media_id,
                },
            },
        }
    }
    await test_utils.update_entries_for("items", item["_id"], {"associations": associations}, item)


async def test_download_single(client, app):
    await setup_image(client, app)
    for _format in wire_formats:
        payload = {"items": [item["_id"]], "format": _format["format"]}
        await HistoryService().delete_many({})
        resp = await client.post("/download", json=payload)
        assert resp.status_code == 200, await resp.get_data(as_text=True)
        assert resp.mimetype == _format["mimetype"]
        assert resp.headers.get("Content-Disposition") in [
            "attachment; filename=%s" % _format["filename"],
            'attachment; filename="%s"' % _format["filename"],
        ]


async def test_wire_download(client, app):
    await setup_image(client, app)
    _file = await test_utils.download_zip_file(client, item_ids, wire_formats[0]["format"], "wire")
    with zipfile.ZipFile(_file) as zf:
        assert wire_formats[0]["filename"] in zf.namelist()
        content = zf.open(wire_formats[0]["filename"]).read()
        if wire_formats[0].get("test_content"):
            wire_formats[0]["test_content"](content)
    history, count = app.data.find("history", None, None)
    assert (len(item_ids)) == count
    assert "download" == history[0]["action"]
    assert history[0].get("user")
    assert history[0].get("versioncreated") + timedelta(seconds=2) >= utcnow()
    assert history[0].get("item") in item_ids
    assert history[0].get("version")
    assert history[0].get("company") is None
    assert history[0].get("section") == "wire"


async def test_agenda_download(client, app):
    await setup_image(client, app)
    payload = {"items": [agenda_items[0]["_id"]], "type": "agenda", "format": agenda_formats[0]["format"]}
    resp = await client.post("/download", json=payload)
    assert resp.status_code == 200, await resp.get_data()
    assert resp.mimetype == agenda_formats[0]["mimetype"]
    if agenda_formats[0].get("test_content"):
        agenda_formats[0]["test_content"](await resp.get_data())
    assert resp.headers.get("content-disposition") == "attachment; filename=%s" % test_utils.get_download_filename(
        agenda_formats[0]["filename"], agenda_items[0]
    )
    history, count = app.data.find("history", None, None)
    assert 1 == count
    assert "download" == history[0]["action"]
    assert history[0].get("user")
    assert history[0].get("versioncreated") + timedelta(seconds=2) >= utcnow()
    assert history[0].get("item") == agenda_items[0]["_id"]
    assert history[0].get("company") is None
