from pytest import fixture
from eve.methods.get import get_internal, getitem_internal
from superdesk import get_resource_service
from flask import g
from bson import ObjectId
from newsroom.tests.fixtures import COMPANY_1_ID, COMPANY_2_ID

company_id = "5c3eb6975f627db90c84093c"


def audit_check(item_id):
    audits = list(get_resource_service("api_audit").find(where={}))
    assert len(audits) == 1
    assert str(audits[0]["items_id"][0]) == item_id


@fixture(autouse=True)
def init(app):
    app.data.insert(
        "companies",
        [{"_id": ObjectId(company_id), "name": "Test Company", "is_enabled": True}],
    )
    app.data.insert(
        "products",
        [
            {
                "_id": ObjectId("5ab03a87bdd78169bb6d0783"),
                "name": "Sample Product X",
                "decsription": "a description",
                "companies": [
                    COMPANY_1_ID,
                    COMPANY_2_ID,
                ],
                "navigations": ["5aa5e94ebdd7810884f66ed3"],
                "sd_product_id": None,
                "product_type": "news_api",
                "query": "fish",
                "is_enabled": True,
            }
        ],
    )


def test_get_item_audit_creation(client, app):
    app.data.insert(
        "items",
        [{"_id": "111", "pubstatus": "usable", "headline": "Headline of the story"}],
    )
    app.data.insert("news_api_tokens", [{"company": ObjectId(company_id), "enabled": True}])
    token = app.data.find_one("news_api_tokens", req=None, company=ObjectId(company_id))
    response = client.get(
        "api/v1/news/item/111?format=NINJSFormatter",
        headers={"Authorization": token.get("token")},
    )
    assert response.status_code == 200
    audit_check("111")


def test_get_all_company_products_audit_creation(client, app):
    with app.test_request_context(path="/account/products/"):
        g.company_id = COMPANY_2_ID
        response = get_internal("account/products")
        assert len(response[0]["_items"]) == 1
        audit_check("5ab03a87bdd78169bb6d0783")


def test_get_single_product_audit_creation(client, app):
    with app.test_request_context(path="/account/products/"):
        g.company_id = COMPANY_2_ID
        response = getitem_internal("account/products", _id="5ab03a87bdd78169bb6d0783")
        assert str(response[0]["_id"]) == "5ab03a87bdd78169bb6d0783"
        audit_check("5ab03a87bdd78169bb6d0783")


def test_search_audit_creation(client, app):
    app.data.insert(
        "items",
        [
            {
                "_id": "5ab03a87bdd78169bb6d0785",
                "body_html": "Once upon a time there was a fish who could swim",
            },
            {"body_html": "Once upon a time there was a aardvark that could not swim"},
        ],
    )
    with app.test_request_context(query_string="q=fish&include_fields=body_html", path="/news"):
        g.company_id = company_id
        response = get_internal("news/search")
        assert len(response[0]["_items"]) == 1
        audit_check("5ab03a87bdd78169bb6d0785")
