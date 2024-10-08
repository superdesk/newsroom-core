from pytest import fixture, raises
from quart import session, json
from eve.utils import ParsedRequest

from superdesk.core import get_app_config
from content_api.errors import BadParameterValueError

from newsroom import auth  # noqa
from newsroom.search.service import SearchQuery, BaseSearchService
from newsroom.search.config import init_nested_aggregation
from newsroom.utils import get_local_date
from newsroom.wire.search import WireSearchResource
from tests.core.utils import create_entries_for

from .fixtures import (
    PUBLIC_USER_ID,
    ADMIN_USER_ID,
    TEST_USER_ID,
    USERS,
    COMPANIES,
    NAV_1,
    NAV_3,
    NAV_5,
    NAVIGATIONS,
    PRODUCTS,
    SECTION_FILTERS,
)

service = BaseSearchService()


@fixture(autouse=True)
async def init(app):
    global service
    service = BaseSearchService()

    app.data.insert("users", USERS)
    app.data.insert("companies", COMPANIES)
    await create_entries_for("navigations", NAVIGATIONS)
    app.data.insert("products", PRODUCTS)
    app.data.insert("section_filters", SECTION_FILTERS)


async def test_apply_section_filter(client, app):
    async with app.test_request_context("/"):
        query_string_settings = get_app_config("ELASTICSEARCH_QUERY_STRING_DEFAULT_PARAMS")
        session["user"] = ADMIN_USER_ID
        search = SearchQuery()
        service.section = "wire"
        service.prefill_search_query(search)
        service.apply_section_filter(search)
        assert {
            "query_string": {
                "query": SECTION_FILTERS[0]["query"],
                "default_operator": "AND",
                "analyze_wildcard": query_string_settings["analyze_wildcard"],
                "lenient": True,
                "fields": ["*"],
                "type": "cross_fields",
            }
        } in search.query["bool"]["filter"]

        search = SearchQuery()
        service.section = "agenda"
        service.prefill_search_query(search)
        service.apply_section_filter(search)
        assert {
            "query_string": {
                "query": SECTION_FILTERS[1]["query"],
                "default_operator": "AND",
                "analyze_wildcard": query_string_settings["analyze_wildcard"],
                "lenient": True,
                "fields": ["*"],
                "type": "cross_fields",
            }
        } in search.query["bool"]["filter"]


async def test_apply_company_filter(client, app):
    app.config["COMPANY_TYPES"] = [
        {"id": "internal", "wire_must": {"term": {"service.code": "a"}}},
        {"id": "public", "wire_must": {"term": {"service.code": "b"}}},
        {"id": "test", "wire_must_not": {"term": {"service.code": "b"}}},
    ]

    async def _set_search_query(user_id):
        async with app.test_request_context("/"):
            session["user"] = user_id
            search = SearchQuery()
            service.prefill_search_user(search)
            service.prefill_search_company(search)
            service.apply_company_filter(search)
            return search.query

    query = await _set_search_query(ADMIN_USER_ID)
    assert {"term": {"service.code": "a"}} not in query["bool"]["filter"]
    assert query["bool"]["must_not"] == []

    query = await _set_search_query(PUBLIC_USER_ID)
    assert query["bool"]["must_not"] == []
    assert {"term": {"service.code": "b"}} in query["bool"]["filter"]

    query = await _set_search_query(TEST_USER_ID)
    assert query["bool"]["filter"] == []
    assert {"term": {"service.code": "b"}} in query["bool"]["must_not"]


async def test_apply_time_limit_filter(client, app):
    app.general_setting("wire_time_limit_days", "wire_time_limit_days", default=25)

    async def _set_search_query(user_id):
        async with app.test_request_context("/"):
            session["user"] = user_id
            search = SearchQuery()
            service.prefill_search_user(search)
            service.prefill_search_company(search)
            service.apply_time_limit_filter(search)
            return search.query["bool"]["filter"]

    assert {"range": {"versioncreated": {"gte": "now-25d/d"}}} not in await _set_search_query(ADMIN_USER_ID)
    assert {"range": {"versioncreated": {"gte": "now-25d/d"}}} not in await _set_search_query(TEST_USER_ID)
    assert {"range": {"versioncreated": {"gte": "now-25d/d"}}} in await _set_search_query(PUBLIC_USER_ID)
    service.limit_days_setting = None
    assert {"range": {"versioncreated": {"gte": "now-25d/d"}}} not in await _set_search_query(PUBLIC_USER_ID)


async def test_apply_products_filter(client, app):
    def assert_products_query(user_id, args=None, products=None):
        query_string_settings = get_app_config("ELASTICSEARCH_QUERY_STRING_DEFAULT_PARAMS")
        session["user"] = user_id
        search = SearchQuery()

        if args is None:
            service.prefill_search_args(search)
            service.prefill_search_query(search)
        else:
            req = ParsedRequest()
            req.args = args
            service.prefill_search_args(search, req)
            service.prefill_search_query(search, req)

        service.apply_products_filter(search)

        for product in products:
            if product.get("query"):
                assert {
                    "query_string": {
                        "query": product["query"],
                        "default_operator": "AND",
                        "analyze_wildcard": query_string_settings["analyze_wildcard"],
                        "lenient": True,
                        "fields": app.config["WIRE_SEARCH_FIELDS"],
                        "type": "cross_fields",
                    }
                } in search.query["bool"]["should"]

        sd_product_ids = [product["sd_product_id"] for product in products if product.get("sd_product_id")]

        if len(sd_product_ids):
            assert {"terms": {"products.code": sd_product_ids}} in search.query["bool"]["should"]

    async with app.test_request_context("/"):
        # Admin has access to everything by default
        assert_products_query(ADMIN_USER_ID, None, [])
        # Filter results by navigation
        assert_products_query(ADMIN_USER_ID, {"navigation": str(NAV_3)}, [PRODUCTS[1]])

        # Public user has access only to their allowed products
        assert_products_query(PUBLIC_USER_ID, None, [PRODUCTS[0], PRODUCTS[1]])
        # Filter results by navigation
        assert_products_query(PUBLIC_USER_ID, {"navigation": str(NAV_1)}, [PRODUCTS[0]])
        # Filter results by navigation, ignoring non wire navigations
        assert_products_query(PUBLIC_USER_ID, {"navigation": "{},{}".format(NAV_1, NAV_5)}, [PRODUCTS[0]])


async def test_apply_request_filter__query_string(client, app):
    query_string_settings = get_app_config("ELASTICSEARCH_QUERY_STRING_DEFAULT_PARAMS")
    search = SearchQuery()
    search.args = {"q": "Sport AND Tennis"}
    service.apply_request_filter(search)
    assert {
        "query_string": {
            "query": "Sport AND Tennis",
            "default_operator": "AND",
            "analyze_wildcard": query_string_settings["analyze_wildcard"],
            "lenient": True,
            "fields": app.config["WIRE_SEARCH_FIELDS"],
            "type": "cross_fields",
        }
    } in search.query["bool"]["must"]

    search.args = {"q": "Sport AND Tennis", "default_operator": "OR"}
    service.apply_request_filter(search)
    assert {
        "query_string": {
            "query": "Sport AND Tennis",
            "default_operator": "OR",
            "analyze_wildcard": query_string_settings["analyze_wildcard"],
            "lenient": True,
            "fields": app.config["WIRE_SEARCH_FIELDS"],
            "type": "cross_fields",
        }
    } in search.query["bool"]["must"]


async def test_apply_request_filter__filters(client, app):
    app.config["FILTER_BY_POST_FILTER"] = False
    app.config["FILTER_AGGREGATIONS"] = True

    search = SearchQuery()
    search.args = {"filter": json.dumps({"service": ["a"]})}
    service.apply_request_filter(search)
    assert {"terms": {"service.name": ["a"]}} in search.query["bool"]["must"]

    search = SearchQuery()
    search.args = {"filter": {"service": ["a"]}}
    service.apply_request_filter(search)
    assert {"terms": {"service.name": ["a"]}} in search.query["bool"]["must"]

    with raises(BadParameterValueError):
        search.args = {"filter": ["test"]}
        service.apply_request_filter(search)

    app.config["FILTER_BY_POST_FILTER"] = False
    app.config["FILTER_AGGREGATIONS"] = False
    search = SearchQuery()
    search.args = {"filter": {"term": {"service": "a"}}}
    service.apply_request_filter(search)
    assert {"term": {"service": "a"}} in search.query["bool"]["must"]

    app.config["FILTER_BY_POST_FILTER"] = True
    app.config["FILTER_AGGREGATIONS"] = True
    search = SearchQuery()
    search.args = {"filter": {"service": ["a"]}}
    service.apply_request_filter(search)
    assert {"terms": {"service.name": ["a"]}} in search.source["post_filter"]["bool"]["must"]

    app.config["FILTER_BY_POST_FILTER"] = True
    app.config["FILTER_AGGREGATIONS"] = False
    search = SearchQuery()
    search.args = {"filter": {"term": {"service": "a"}}}
    service.apply_request_filter(search)
    assert {"term": {"service": "a"}} in search.source["post_filter"]["bool"]["must"]


async def test_apply_request_filter__filters_using_groups_config(client, app):
    app.config["FILTER_BY_POST_FILTER"] = False
    app.config["FILTER_AGGREGATIONS"] = True
    app.config["WIRE_GROUPS"] = [
        {
            "field": "testfield",
            "label": "Test Field",
            "nested": {
                "parent": "subject",
                "field": "scheme",
                "value": "testfieldscheme",
            },
        },
    ]
    init_nested_aggregation(WireSearchResource, app.config["WIRE_GROUPS"], {})

    search = SearchQuery()
    search.args = {"filter": json.dumps({"testfield": ["valuea", "valueb"]})}
    service.apply_request_filter(search)
    assert {
        "nested": {
            "path": "subject",
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"subject.scheme": "testfieldscheme"}},
                        {"terms": {"subject.name": ["valuea", "valueb"]}},
                    ],
                },
            },
        },
    } in search.query["bool"]["must"]


async def test_apply_request_filter__versioncreated(client, app):
    app.config["FILTER_BY_POST_FILTER"] = False

    search = SearchQuery()
    search.args = {"created_from": "2020-03-27"}
    service.apply_request_filter(search)
    assert {"range": {"versioncreated": {"gte": get_local_date("2020-03-27", "00:00:00", 0)}}} in search.query["bool"][
        "must"
    ]

    search = SearchQuery()
    search.args = {"created_to": "2020-03-27"}
    service.apply_request_filter(search)
    assert {"range": {"versioncreated": {"lte": get_local_date("2020-03-27", "23:59:59", 0)}}} in search.query["bool"][
        "must"
    ]

    search = SearchQuery()
    search.args = {
        "created_from": "2020-03-27",
        "created_from_time": "01:12:45",
        "created_to": "2020-03-27",
    }
    service.apply_request_filter(search)
    assert {
        "range": {
            "versioncreated": {
                "gte": get_local_date("2020-03-27", "01:12:45", 0),
                "lte": get_local_date("2020-03-27", "23:59:59", 0),
            }
        }
    } in search.query["bool"]["must"]

    app.config["FILTER_BY_POST_FILTER"] = True

    search = SearchQuery()
    search.args = {"created_from": "2020-03-27"}
    service.apply_request_filter(search)
    assert {"range": {"versioncreated": {"gte": get_local_date("2020-03-27", "00:00:00", 0)}}} in search.source[
        "post_filter"
    ]["bool"]["must"]

    search = SearchQuery()
    search.args = {"created_to": "2020-03-27"}
    service.apply_request_filter(search)
    assert {"range": {"versioncreated": {"lte": get_local_date("2020-03-27", "23:59:59", 0)}}} in search.source[
        "post_filter"
    ]["bool"]["must"]

    search = SearchQuery()
    search.args = {
        "created_from": "2020-03-27",
        "created_from_time": "01:12:45",
        "created_to": "2020-03-27",
    }
    service.apply_request_filter(search)
    assert {
        "range": {
            "versioncreated": {
                "gte": get_local_date("2020-03-27", "01:12:45", 0),
                "lte": get_local_date("2020-03-27", "23:59:59", 0),
            }
        }
    } in search.source["post_filter"]["bool"]["must"]
