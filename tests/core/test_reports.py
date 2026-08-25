from quart import json
from pytest import fixture
from bson import ObjectId
from datetime import datetime, timedelta
from newsroom.tests.fixtures import COMPANY_1_ID
from tests.core.utils import create_entries_for, update_entries_for
from ..fixtures import items


@fixture(autouse=True)
async def init(app):
    await create_entries_for(
        "auth_user",
        [
            {
                "_id": ObjectId("5cc94454bc43165c045ffec0"),
                "email": "foo@foo.com",
                "first_name": "Foo",
                "last_name": "Smith",
                "is_enabled": True,
                "company": COMPANY_1_ID,
            },
            {
                "_id": ObjectId("5cc94454bc43165c045ffec1"),
                "email": "bar@bar.com",
                "first_name": "Bar",
                "last_name": "Brown",
                "is_enabled": True,
            },
            {
                "_id": ObjectId("5cc94454bc43165c045ffec2"),
                "email": "baz@bar.com",
                "first_name": "Bar",
                "last_name": "Brown",
                "is_enabled": True,
                "company": COMPANY_1_ID,
            },
        ],
    )
    await create_entries_for(
        "products",
        [
            {
                "_id": ObjectId("5e65964bf5db68883df561d1"),
                "name": "Sport",
                "description": "sport product",
                "is_enabled": True,
                "product_type": "agenda",
            },
            {
                "_id": ObjectId("6e65964bf5db68883df561d1"),
                "name": "News",
                "description": "news product",
                "is_enabled": True,
                "product_type": "wire",
            },
        ],
    )
    await create_entries_for(
        "companies",
        [
            {
                "_id": ObjectId(),
                "name": "Example Company",
                "is_enabled": True,
                "sections": {"wire": True},
                "products": [
                    {"_id": ObjectId("5e65964bf5db68883df561d1"), "section": "wire"},
                ],
            },
            {
                "_id": ObjectId(),
                "name": "Example 2 Company",
                "is_enabled": True,
                "sections": {"wire": True},
                "products": [
                    {"_id": ObjectId("6e65964bf5db68883df561d1"), "section": "wire"},
                ],
            },
        ],
    )


async def test_company_saved_searches(client, app):
    await create_entries_for(
        "topics",
        [
            {
                "_id": ObjectId(),
                "label": "Foo",
                "query": "foo",
                "topic_type": "wire",
                "user": "5cc94454bc43165c045ffec0",
            },
            {
                "_id": ObjectId(),
                "label": "Foo",
                "query": "foo",
                "topic_type": "wire",
                "user": "5cc94454bc43165c045ffec1",
            },
            {
                "_id": ObjectId(),
                "label": "Foo",
                "query": "foo",
                "topic_type": "wire",
                "user": "5cc94454bc43165c045ffec2",
            },
        ],
    )
    resp = await client.get("reports/company-saved-searches")
    report = json.loads(await resp.get_data())
    assert report["name"] == "Saved searches per company"
    assert len(report["results"]) == 1
    assert report["results"][0]["name"] == "Press Co."
    assert report["results"][0]["topic_count"] == 2


async def test_user_saved_searches(client, app):
    await create_entries_for(
        "topics",
        [
            {
                "_id": ObjectId(),
                "label": "Foo",
                "query": "foo",
                "topic_type": "wire",
                "user": ObjectId("5cc94454bc43165c045ffec0"),
            },
            {
                "_id": ObjectId(),
                "label": "Foo",
                "query": "foo",
                "topic_type": "wire",
                "user": ObjectId("5cc94454bc43165c045ffec1"),
            },
            {
                "_id": ObjectId(),
                "label": "Foo",
                "query": "foo",
                "topic_type": "wire",
                "user": ObjectId("5cc94454bc43165c045ffec0"),
            },
        ],
    )

    resp = await client.get("reports/user-saved-searches")
    report = json.loads(await resp.get_data())
    assert report["name"] == "Saved searches per user"
    assert len(report["results"]) == 1
    assert report["results"][0]["name"] == "Foo Smith"
    assert report["results"][0]["topic_count"] == 2


async def test_company_products(client):
    resp = await client.get("reports/company-products")
    report = json.loads(await resp.get_data())
    assert report["name"] == "Products per company"
    assert len(report["results"]) == 5
    assert report["results"][0]["name"] == "Example 2 Company"
    assert len(report["results"][0]["products"]) == 1
    assert report["results"][1]["name"] == "Example Company"
    assert len(report["results"][1]["products"]) == 1


async def test_product_companies(client):
    resp = await client.get("reports/product-companies")
    report = json.loads(await resp.get_data())
    assert report["name"] == "Companies permissioned per product"
    assert len(report["results"]) == 2
    assert report["results"][0]["product"] == "News"
    assert len(report["results"][0]["enabled_companies"]) == 1
    assert report["results"][1]["product"] == "Sport"
    assert len(report["results"][1]["enabled_companies"]) == 1


async def test_expired_companies(client, app):
    await create_entries_for(
        "companies",
        [
            {
                "_id": ObjectId("5cd0e0b35f627d400e8b7566"),
                "name": "Expired and enabled Co.",
                "is_enabled": True,
                "expiry_date": datetime.utcnow() - timedelta(days=1),
            },
            {
                "_id": ObjectId("5b504318975bd5227e5ea0b9"),
                "name": "Expired disabled Co.",
                "expiry_date": datetime.utcnow() - timedelta(days=10),
                "is_enabled": False,
            },
        ],
    )
    resp = await client.get("reports/expired-companies")
    report = json.loads(await resp.get_data())
    assert report["name"] == "Expired companies"
    assert len(report["results"]) == 2


async def test_companies(client):
    resp = await client.get("reports/company")
    report = json.loads(await resp.get_data())
    assert report["name"] == "Company"
    assert len(report["results"]) == 5
    assert report["results"][0]["name"] == "Example 2 Company"
    assert report["results"][1]["name"] == "Example Company"
    assert report["results"][2]["name"] == "News Co."
    assert report["results"][3]["name"] == "Paper Co."


async def test_product_stories(client):
    # sd_product_id matches an item's products.code: "1" -> tag:foo (today),
    # "7" -> urn:localhost:flood (~5 days ago)
    await create_entries_for(
        "products",
        [
            {
                "_id": ObjectId("5e65964bf5db68883df56201"),
                "name": "Wire Product A",
                "sd_product_id": "1",
                "is_enabled": True,
                "product_type": "wire",
            },
            {
                "_id": ObjectId("5e65964bf5db68883df56202"),
                "name": "Wire Product B",
                "sd_product_id": "7",
                "is_enabled": True,
                "product_type": "wire",
            },
        ],
    )

    resp = await client.get("reports/product-stories")
    report = json.loads(await resp.get_data())
    assert report["name"] == "Stories per product"

    results = {result["name"]: result for result in report["results"]}
    product_a = results["Wire Product A"]
    product_b = results["Wire Product B"]

    # Counts must be scoped per product, not whole-index totals
    assert product_a["today"] == 1
    assert product_a["last_7_days"] == 1
    assert product_a["last_6_months"] == 1

    assert product_b["today"] == 0
    assert product_b["last_7_days"] == 1
    assert product_b["last_6_months"] == 1


async def test_content_activity_csv(client):
    today = datetime.now().date()

    for item in items:
        if item.get("_id") == "tag:weather":
            await update_entries_for(
                "items",
                item["_id"],
                {"versioncreated": datetime.now() + timedelta(minutes=1), "headline": "New weather"},
                item,
            )
        if item.get("_id") == "tag:weather:old":
            await update_entries_for(
                "items",
                item["_id"],
                {"versioncreated": datetime.now() + timedelta(minutes=2), "headline": "Old weather"},
                item,
            )

    resp = await client.get(
        "reports/export/content-activity?export=true&date_from={}&date_to={}".format(
            today.isoformat(), today.isoformat()
        )
    )
    assert 200 == resp.status_code

    report = await resp.get_data(as_text=True)
    lines = report.splitlines()
    assert len(lines) > 1

    fields = lines[0].split(",")
    assert "Headline" == fields[1]

    values = lines[1].split(",")
    assert "Amazon Is Opening More Bookstores" == values[1]
    assert "0" == values[-1]
    assert "New weather" == lines[2].split(",")[1]
    assert "Old weather" == lines[3].split(",")[1]
