from pytest import fixture, raises
from flask import session
from eve.utils import ParsedRequest
from werkzeug.datastructures import ImmutableMultiDict

from content_api.errors import BadParameterValueError

from newsroom import auth  # noqa
from newsroom.search.service import SearchQuery, BaseSearchService

from .fixtures import (
    PUBLIC_USER_ID,
    ADMIN_USER_ID,
    TEST_USER_ID,
    USERS,
    COMPANY_1,
    COMPANY_2,
    COMPANY_3,
    COMPANIES,
    NAV_1,
    NAV_2,
    NAV_3,
    NAV_4,
    NAV_5,
    NAV_6,
    NAVIGATIONS,
    PROD_1,
    PROD_2,
    PROD_3,
    PRODUCTS,
)

service = BaseSearchService()


@fixture(autouse=True)
def init(app):
    global service
    service = BaseSearchService()

    app.data.insert("users", USERS)
    app.data.insert("companies", COMPANIES)
    app.data.insert("navigations", NAVIGATIONS)
    app.data.insert("products", PRODUCTS)


def get_search_instance(args=None, lookup=None):
    search = SearchQuery()

    if not args:
        service.prefill_search_args(search, req=None)
        service.prefill_search_query(search, req=None, lookup=lookup)
    else:
        req = ParsedRequest()
        req.args = args
        service.prefill_search_args(search, req)
        service.prefill_search_query(search, req, lookup)

    return search


def test_prefill_search_args(client, app):
    with app.test_request_context():
        search = SearchQuery()
        service.prefill_search_args(search)
        assert search.args == {
            "embargoed_only": False,
            "exclude_embargoed": False,
            "newsOnly": False,
        }
        assert search.projections == {}
        assert search.req is None

        search = SearchQuery()
        req = ParsedRequest()
        req.args = {"test": "one"}
        service.prefill_search_args(search, req)
        assert search.args == {
            "test": "one",
            "embargoed_only": False,
            "exclude_embargoed": False,
            "newsOnly": False,
        }
        assert search.projections == {}
        assert search.req == req

        search = SearchQuery()
        req = ParsedRequest()
        req.args = ImmutableMultiDict([("foo", "bar"), ("name", "test")])
        service.prefill_search_args(search, req)
        assert search.args == {
            "foo": "bar",
            "name": "test",
            "embargoed_only": False,
            "exclude_embargoed": False,
            "newsOnly": False,
        }
        assert search.projections == {}
        assert search.req == req

        search = SearchQuery()
        req = ParsedRequest()
        req.projection = {"service": 1}
        service.prefill_search_args(search, req)
        assert search.args == {
            "embargoed_only": False,
            "exclude_embargoed": False,
            "newsOnly": False,
        }
        assert search.projections == {"service": 1}
        assert search.req == req


def test_prefill_search_lookup(client, app):
    with app.test_request_context():
        search = get_search_instance()
        assert search.lookup == {}

        search = get_search_instance(lookup={})
        assert search.lookup == {}

        search = get_search_instance(lookup={"foo": "bar"})
        assert search.lookup == {"foo": "bar"}


def test_prefill_search_page(client, app):
    with app.test_request_context():
        search = get_search_instance()
        assert search.args == {
            "sort": service.default_sort,
            "size": service.default_page_size,
            "from": 0,
            "embargoed_only": False,
            "exclude_embargoed": False,
            "newsOnly": False,
        }

        search = get_search_instance(
            args={
                "sort": [{"versioncreated": "asc"}],
                "size": "50",
                "from": "50",
            }
        )
        assert search.args == {
            "sort": [{"versioncreated": "asc"}],
            "size": 50,
            "from": 50,
            "embargoed_only": False,
            "exclude_embargoed": False,
            "newsOnly": False,
        }


def test_prefill_search_user(client, app):
    with app.test_request_context():
        session["user"] = None
        search = get_search_instance()
        assert search.user is None

        session["user"] = ADMIN_USER_ID
        search = get_search_instance()
        assert search.user.get("_id") == ADMIN_USER_ID
        assert search.is_admin is True

        session["user"] = PUBLIC_USER_ID
        search = get_search_instance()
        assert search.user.get("_id") == PUBLIC_USER_ID
        assert search.is_admin is False

        session["user"] = ADMIN_USER_ID
        search = get_search_instance(args={"user": TEST_USER_ID})
        assert search.user.get("_id") == TEST_USER_ID
        assert search.is_admin is False


def test_prefill_search_company(client, app):
    with app.test_request_context():
        session["user"] = None
        search = get_search_instance()
        assert search.user is None
        assert search.company is None

        session["user"] = ADMIN_USER_ID
        search = get_search_instance()
        assert search.company.get("_id") == COMPANY_1

        session["user"] = PUBLIC_USER_ID
        search = get_search_instance()
        assert search.company.get("_id") == COMPANY_2

        session["user"] = ADMIN_USER_ID
        search = get_search_instance(args={"user": TEST_USER_ID})
        assert search.company.get("_id") == COMPANY_3


def test_prefill_search_section(client, app):
    with app.test_request_context():
        search = get_search_instance()
        assert search.section == service.section

        service.section = "test"
        search = get_search_instance()
        assert search.section == "test"


def test_prefill_search_navigation(client, app):
    with app.test_request_context():
        search = get_search_instance()
        assert search.navigation_ids == []

        search = get_search_instance(args={"navigation": ""})
        assert search.navigation_ids == []

        search = get_search_instance(args={"navigation": "{},{},{}".format(NAV_1, NAV_2, NAV_3)})
        assert search.navigation_ids == [str(NAV_1), str(NAV_2), str(NAV_3)]

        search = get_search_instance(args={"navigation": [str(NAV_1), str(NAV_2), str(NAV_3)]})
        assert search.navigation_ids == [str(NAV_1), str(NAV_2), str(NAV_3)]

        with raises(BadParameterValueError):
            get_search_instance(args={"navigation": {"test": NAV_1}})


def test_prefill_search_products__requested_products(client, app):
    with app.test_request_context():
        search = get_search_instance()
        assert search.requested_products == []

        search = get_search_instance(args={"requested_products": "{},{},{}".format(PROD_1, PROD_2, PROD_3)})
        assert search.requested_products == [str(PROD_1), str(PROD_2), str(PROD_3)]

        search = get_search_instance(args={"requested_products": [str(PROD_1), str(PROD_2), str(PROD_3)]})
        assert search.requested_products == [str(PROD_1), str(PROD_2), str(PROD_3)]

        with raises(BadParameterValueError):
            get_search_instance(args={"requested_products": {"test": PROD_3}})


def test_prefill_search_products__admin_products(client, app):
    with app.test_request_context():
        session["user"] = ADMIN_USER_ID
        search = get_search_instance()
        assert search.products == []

        search = get_search_instance(
            args={
                "navigation": [
                    NAV_1,  # PROD_1: enabled for Admin/Company
                    NAV_3,  # PROD_2: not enabled for Admin/Company
                    NAV_4,  # PROD_3: is_enabled=False
                    NAV_5,  # PROD_4: product_type=agenda
                ]
            }
        )
        assert len(search.products) == 2
        assert search.products[0]["_id"] in [PROD_1, PROD_2]
        assert search.products[1]["_id"] in [PROD_1, PROD_2]


def test_prefill_search_products__public_products(client, app):
    with app.test_request_context():
        session["user"] = PUBLIC_USER_ID
        search = get_search_instance()
        assert len(search.products) == 2
        assert search.products[0]["_id"] in [PROD_1, PROD_2]
        assert search.products[1]["_id"] in [PROD_1, PROD_2]

        search = get_search_instance(
            args={
                "navigation": [
                    NAV_1,  # PROD_1: enabled for Public/Company
                    NAV_2,  # PROD_1: enabled for Public/Company
                    NAV_3,  # PROD_2: enabled for Public/Company
                    NAV_4,  # PROD_3: is_enabled=False
                    NAV_5,  # PROD_4: product_type=agenda
                    NAV_6,  # PROD_4: disabled for Public/Company
                ]
            }
        )
        assert len(search.products) == 2
        assert search.products[0]["_id"] in [PROD_1, PROD_2]
        assert search.products[1]["_id"] in [PROD_1, PROD_2]


def test_prefill_search_items(client, app):
    with app.test_request_context():
        search = get_search_instance()
        assert {"term": {"type": "composite"}} in search.query["bool"]["must_not"]
        assert {"constant_score": {"filter": {"exists": {"field": "nextversion"}}}} in search.query["bool"]["must_not"]

        search = get_search_instance(args={"ignore_latest": True})
        assert {"constant_score": {"filter": {"exists": {"field": "nextversion"}}}} not in search.query["bool"][
            "must_not"
        ]
