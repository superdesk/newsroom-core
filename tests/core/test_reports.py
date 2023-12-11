from flask import json
from pytest import fixture
from bson import ObjectId
from datetime import datetime, timedelta
from newsroom.tests.fixtures import COMPANY_1_ID


@fixture(autouse=True)
def init(app):
    app.data.insert(
        "users",
        [
            {
                "_id": "u-1",
                "email": "foo@foo.com",
                "first_name": "Foo",
                "last_name": "Smith",
                "is_enabled": True,
                "company": COMPANY_1_ID,
            },
            {
                "_id": "u-2",
                "email": "bar@bar.com",
                "first_name": "Bar",
                "last_name": "Brown",
                "is_enabled": True,
            },
            {
                "_id": "u-3",
                "email": "baz@bar.com",
                "first_name": "Bar",
                "last_name": "Brown",
                "is_enabled": True,
                "company": COMPANY_1_ID,
            },
        ],
    )
    app.data.insert(
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
    app.data.insert(
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


def test_company_saved_searches(client, app):
    app.data.insert(
        "topics",
        [
            {"label": "Foo", "query": "foo", "notifications": False, "user": "u-1"},
            {"label": "Foo", "query": "foo", "notifications": False, "user": "u-2"},
            {"label": "Foo", "query": "foo", "notifications": False, "user": "u-3"},
        ],
    )

    resp = client.get("reports/company-saved-searches")
    report = json.loads(resp.get_data())
    assert report["name"] == "Saved searches per company"
    assert len(report["results"]) == 1
    assert report["results"][0]["name"] == "Press Co."
    assert report["results"][0]["topic_count"] == 2


def test_user_saved_searches(client, app):
    app.data.insert(
        "topics",
        [
            {"label": "Foo", "query": "foo", "notifications": False, "user": "u-1"},
            {"label": "Foo", "query": "foo", "notifications": False, "user": "u-2"},
            {"label": "Foo", "query": "foo", "notifications": False, "user": "u-1"},
        ],
    )

    resp = client.get("reports/user-saved-searches")
    report = json.loads(resp.get_data())
    assert report["name"] == "Saved searches per user"
    assert len(report["results"]) == 1
    assert report["results"][0]["name"] == "Foo Smith"
    assert report["results"][0]["topic_count"] == 2


def test_company_products(client):
    resp = client.get("reports/company-products")
    report = json.loads(resp.get_data())
    assert report["name"] == "Products per company"
    assert len(report["results"]) == 4
    assert report["results"][0]["name"] == "Example 2 Company"
    assert len(report["results"][0]["products"]) == 1
    assert report["results"][1]["name"] == "Example Company"
    assert len(report["results"][1]["products"]) == 1


def test_product_companies(client):
    resp = client.get("reports/product-companies")
    report = json.loads(resp.get_data())
    assert report["name"] == "Companies permissioned per product"
    assert len(report["results"]) == 2
    assert report["results"][0]["product"] == "News"
    assert len(report["results"][0]["enabled_companies"]) == 1
    assert report["results"][1]["product"] == "Sport"
    assert len(report["results"][1]["enabled_companies"]) == 1


def test_expired_companies(client, app):
    app.data.insert(
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
    resp = client.get("reports/expired-companies")
    report = json.loads(resp.get_data())
    assert report["name"] == "Expired companies"
    assert len(report["results"]) == 2


def test_companies(client):
    resp = client.get("reports/company")
    report = json.loads(resp.get_data())
    assert report["name"] == "Company"
    assert len(report["results"]) == 4
    assert report["results"][0]["name"] == "Example 2 Company"
    assert report["results"][1]["name"] == "Example Company"
    assert report["results"][2]["name"] == "Paper Co."
