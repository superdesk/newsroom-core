import logging
from typing import List, Optional, Union, Dict, Any, TypedDict
from copy import deepcopy

from flask import current_app as app, json, abort
from flask_babel import gettext
from eve.utils import ParsedRequest
from werkzeug.exceptions import Forbidden

from superdesk import get_resource_service
from superdesk.metadata.utils import get_elastic_highlight_query
from superdesk.default_settings import strtobool as _strtobool
from content_api.errors import BadParameterValueError

from newsroom import Service
from newsroom.search.config import SearchGroupNestedConfig, get_nested_config, is_search_field_nested
from newsroom.products.products import (
    get_products_by_navigation,
    get_products_by_company,
    get_product_by_id,
    get_products_by_user,
)
from newsroom.auth import get_company, get_user
from newsroom.settings import get_setting
from newsroom.template_filters import is_admin
from newsroom.utils import get_local_date, get_end_date
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)


def strtobool(val):
    if isinstance(val, bool):
        return val
    return _strtobool(val)


def query_string(query, default_operator="AND"):
    query_string_settings = app.config["ELASTICSEARCH_SETTINGS"]["settings"]["query_string"]
    return {
        "query_string": {
            "query": query,
            "default_operator": default_operator,
            "analyze_wildcard": query_string_settings["analyze_wildcard"],
            "lenient": True,
        }
    }


def get_filter_query(
    key: str, val: List[str], aggregation_field: str, nested_config: Optional[SearchGroupNestedConfig]
):
    if nested_config:
        return {
            "nested": {
                "path": nested_config["parent"],
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {f"{nested_config['parent']}.{nested_config['field']}": nested_config["value"]}},
                            {"terms": {f"{nested_config['parent']}.{nested_config['searchfield']}": val}},
                        ],
                    },
                },
            },
        }
    return {"terms": {aggregation_field: val}}


class AdvancedSearchParams(TypedDict):
    all: str
    any: str
    exclude: str
    fields: List[str]


class SearchQuery(object):
    """Class for storing the search parameters for validation and query generation"""

    def __init__(self):
        self.user = None
        self.is_admin = False
        self.company = None

        self.section = None
        self.navigation_ids = []
        self.products = []
        self.requested_products = []
        self.advanced: AdvancedSearchParams = {
            "all": "",
            "any": "",
            "exclude": "",
            "fields": [],
        }

        self.args = {}
        self.lookup = {}
        self.projections = {}
        self.req = None

        self.aggs = None
        self.source = {}
        self.query = {"bool": {"filter": [], "must_not": [], "should": []}}
        self.highlight = None
        self.item_type = None
        self.planning_items_should = []


class BaseSearchService(Service):
    section = "wire"
    limit_days_setting: Union[None, str] = "wire_time_limit_days"
    default_sort = [{"versioncreated": "desc"}]
    default_page_size = 25
    _matched_ids = []  # array of IDs matched on the request, used when searching all versions
    default_advanced_search_fields = []

    def get(self, req, lookup):
        search = SearchQuery()
        self.prefill_search_args(search, req)

        if search.args.get("all_versions"):
            response = self._search_all_versions(search, req, lookup)
        else:
            self.prefill_search_query(search, req, lookup)
            self.validate_request(search)
            self.apply_filters(search)
            self.gen_source_from_search(search)

            internal_req = self.get_internal_request(search)
            response = self.internal_get(internal_req, search.lookup)

        if search.args.get("prepend_embargoed"):
            self.prepend_embargoed_items_to_response(response, req, lookup)

        return response

    def on_fetched(self, docs):
        """Add IDs of the versions that matched the search to the HATEOAS response

        The list of IDs are not guaranteed to be in the ``_items`` response.
        This is used in the front-end to highlight which version matched the search query,
        which may not be the last version in the content chain.
        """

        if self._matched_ids:
            docs["_links"]["matched_ids"] = self._matched_ids
            self._matched_ids = []

    def _search_all_versions(self, search: SearchQuery, req, lookup):
        """Search across all versions of items, but return last versions only"""

        search.args["ignore_latest"] = True
        self.prefill_search_query(search, req, lookup)
        self.validate_request(search)
        self.apply_filters(search)
        self.gen_source_from_search(search)

        # Search up to 1,000 items to make sure pagination works
        # as we're getting all versions here
        # where as the final response will only include the last version
        # of each content chain
        search.source["size"] = 1000
        search.source["from"] = 0

        internal_req = self.get_internal_request(search)
        search_results = self.internal_get(internal_req, search.lookup)
        next_item_ids = []
        self._matched_ids = []

        for doc in search_results.docs:
            self._matched_ids.append(doc["_id"])
            next_item_ids.append(str(self.get_last_version(doc)["_id"]))

        # Now run a query only using the IDs from the above search
        # This final search makes sure pagination still works
        search.query["bool"] = {"filter": {"terms": {"_id": next_item_ids}}}
        self.gen_source_from_search(search)
        internal_req = self.get_internal_request(search)
        res = self.internal_get(internal_req, search.lookup)
        # count including previous versions
        res.hits["hits"]["total"] = search_results.count()
        return res

    def get_last_version(self, doc):
        if not doc.get("nextversion"):
            # This is already the latest version
            return doc
        elif doc.get("original_id"):
            # Attempt to get the last version in the series using Elastic
            original_id = doc["original_id"]
            req = ParsedRequest()
            req.args = {
                "source": json.dumps(
                    {
                        "query": {
                            "bool": {
                                "filter": [
                                    {"term": {"original_id": original_id}},
                                ],
                                "must_not": [{"exists": {"field": "nextversion"}}],
                            }
                        }
                    }
                ),
                "size": 1,
            }
            result = self.internal_get(req=req, lookup=None)

            if result.count():
                return result[0]
            else:
                logger.warning(f'Failed to find the latest version using `original_id="{original_id}"`')

        # Either the item doesn't have ``original_id`` set, or the elastic query didn't find a match
        # So we resort to a slower method
        # This can happen for item's that were published prior to this new feature
        nextversion_id = doc["nextversion"]
        next_doc = self.find_one(req=None, _id=nextversion_id)
        if next_doc:
            return self.get_last_version(next_doc)
        else:
            # If, for whatever reason, we can't get the next version return the current one.
            # That way the request will still be fulfilled,
            # albeit with this content group cut short in versions
            item_id = doc["_id"]
            logger.warning(f'Failed to find the next doc "{nextversion_id}" for "{item_id}"')
            return doc

    def internal_get(self, req, lookup):
        return super().get(req, lookup)

    # Overridable internal methods
    def prefill_search_query(self, search, req=None, lookup=None):
        """Generate the search query instance

        :param SearchQuery search: The search query instance
        :param ParsedRequest req: The parsed in request instance from the endpoint
        :param dict lookup: The parsed in lookup dictionary from the endpoint
        """

        self.prefill_search_lookup(search, lookup)
        self.prefill_search_page(search)
        self.prefill_search_user(search)
        self.prefill_search_company(search)
        self.prefill_search_section(search)
        self.prefill_search_navigation(search)
        self.prefill_search_products(search)
        self.prefill_search_items(search)
        self.prefill_search_highlights(search, req)

    def apply_filters(self, search):
        """Generate and apply the different search filters

        :param SearchQuery search: the search query instance
        """
        self.apply_section_filter(search)
        self.apply_company_filter(search)
        self.apply_time_limit_filter(search)
        self.apply_products_filter(search)
        self.apply_request_filter(search)
        self.apply_request_advanced_search(search)
        self.apply_embargoed_filters(search)

        if len(search.query["bool"].get("should", [])):
            search.query["bool"]["minimum_should_match"] = 1

    def gen_source_from_search(self, search):
        """Generate the eve source object from the search query instance

        :param SearchQuery search: The search query instance
        """

        search.source["query"] = search.query
        search.source["sort"] = search.args.get("sort") or self.default_sort
        search.source["size"] = int(search.args.get("size", self.default_page_size))
        search.source["from"] = int(search.args.get("from", 0))

        if search.source["from"] >= 1000:
            # https://www.elastic.co/guide/en/elasticsearch/guide/current/pagination.html#pagination
            return abort(400, gettext("Page limit exceeded"))

        if not search.source["from"] and strtobool(search.args.get("aggs", "true")):
            search.source["aggs"] = self.get_aggregations()

        if search.highlight:
            search.source["highlight"] = search.highlight

    def get_internal_request(self, search):
        """Creates an eve internal request object

        :param SearchQuery search: the search query instnace
        :return:
        """
        internal_req = ParsedRequest()
        internal_req.args = {"source": json.dumps(search.source)}

        if search.projections:
            internal_req.args["projections"] = search.projections
            internal_req.projection = search.projections

        return internal_req

    def set_bool_query_from_filters(self, bool_query: Dict[str, Any], filters: Dict[str, Any]):
        for key, val in filters.items():
            if not val:
                continue
            bool_query["filter"].append(
                get_filter_query(key, val, self.get_aggregation_field(key), get_nested_config("items", key))
            )

    def get_aggregations(self):
        return app.config.get("WIRE_AGGS") or {}

    def get_aggregation_field(self, key):
        aggregations = self.get_aggregations()
        if key not in aggregations:
            return key
        if is_search_field_nested("items", key):
            return aggregations[key]["aggs"][f"{key}_filtered"]["aggs"][key]["terms"]["field"]
        else:
            return aggregations[key]["terms"]["field"]

    def versioncreated_range(self, created):
        _range = {}
        offset = int(created.get("timezone_offset", "0"))
        if created.get("created_from"):
            _range["gte"] = get_local_date(
                created["created_from"],
                created.get("created_from_time", "00:00:00"),
                offset,
            )
        if created.get("created_to"):
            _range["lte"] = get_end_date(
                created["created_to"],
                get_local_date(created["created_to"], "23:59:59", offset),
            )
        return {"range": {"versioncreated": _range}}

    def prefill_search_args(self, search, req=None):
        """Prefill the search request args

        :param SearchQuery search: The search query instance
        :param ParsedRequest req: The passed in request instance
        """

        if req is None:
            search.args = {}
        elif getattr(req.args, "to_dict", None):
            search.args = deepcopy(req.args.to_dict())
        elif isinstance(req.args, dict):
            search.args = deepcopy(req.args)
        else:
            search.args = {}

        search.projections = {} if req is None or not req.projection else req.projection
        search.req = req

        if search.args.get("prepend_embargoed"):
            # Exclude embargoed items if we're prepending them anyway
            search.args.update(
                {
                    "exclude_embargoed": True,
                    "embargoed_only": False,
                }
            )
        else:
            search.args["exclude_embargoed"] = strtobool(str(search.args.get("exclude_embargoed", False)))
            search.args["embargoed_only"] = strtobool(str(search.args.get("embargoed_only", False)))

        search.args["newsOnly"] = strtobool(str(search.args.get("newsOnly", False)))

    def prefill_search_lookup(self, search, lookup=None):
        """Prefill the search lookup

        :param SearchQuery search: the search query instance
        :param dict lookup: the lookup dictionary provided by the endpoint
        """

        search.lookup = {} if lookup is None else lookup

    def prefill_search_user(self, search):
        """Prefill the search user

        :param SearchQuery search: The search query instance
        """

        current_user = get_user(required=False)
        search.is_admin = is_admin(current_user)

        if search.is_admin and search.args.get("user"):
            search.user = get_resource_service("users").find_one(req=None, _id=search.args["user"])
            search.is_admin = is_admin(search.user)
        else:
            search.user = current_user

    def prefill_search_company(self, search):
        """Prefill the search company

        :param SearchQuery search: The search query instance
        """

        search.company = get_company(search.user)

    def prefill_search_page(self, search):
        """Prefill the search page parameters

        :param SearchQuery search: The search query instance
        :param ParsedRequest req: The parsed in request instance from the endpoint
        """

        if not search.args.get("sort"):
            search.args["sort"] = search.req.sort if search.req is not None and search.req.sort else self.default_sort

        search.args["size"] = int(search.args.get("size", self.default_page_size))
        search.args["from"] = int(search.args.get("from", 0))

    def prefill_search_section(self, search):
        """Prefill the search section

        :param SearchQuery search: The search query instance
        """

        search.section = search.args.get("section") or self.section

    def prefill_search_navigation(self, search):
        """Prefill the search navigation

        :param SearchQuery search: The search query instance
        """

        if search.args.get("navigation"):
            navigation = search.args["navigation"]
            if isinstance(navigation, list):
                search.navigation_ids = navigation
            elif getattr(navigation, "split", None):
                search.navigation_ids = list(navigation.split(","))
            else:
                raise BadParameterValueError("Invalid navigation parameter")
        else:
            search.navigation_ids = []

    def prefill_search_products(self, search):
        """Prefill the search products

        :param SearchQuery search: The search query instance
        """

        if search.args.get("requested_products"):
            products = search.args["requested_products"]
            if isinstance(products, list):
                search.requested_products = products
            elif getattr(products, "split", None):
                search.requested_products = list(products.split(","))
            else:
                raise BadParameterValueError("Invalid requested_products parameter")

        if search.is_admin:
            if len(search.navigation_ids):
                search.products = get_products_by_navigation(search.navigation_ids, product_type=search.section)
            elif search.args.get("product"):
                search.products = get_product_by_id(search.args["product"], product_type=search.section)
            else:
                # admin will see everything by default,
                # regardless of company products
                search.products = []
        elif search.company:
            if search.args.get("product"):
                search.products = get_product_by_id(
                    search.args["product"],
                    product_type=search.section,
                )

            else:
                search.products = []

                if search.user and search.user.get("products"):
                    user_products = get_products_by_user(
                        search.user,
                        search.section,
                    )

                    if user_products:
                        # User has Products assigned
                        search.products += user_products

                # add unlimited (seats=0) company products
                company_products = get_products_by_company(
                    search.company,
                    search.navigation_ids,
                    product_type=search.section,
                    unlimited_only=True,
                )

                if company_products:
                    for product in company_products:
                        if product not in search.products:
                            search.products.append(product)

        else:
            search.products = []

    def prefill_search_items(self, search):
        """Prefill the item filters

        :param SearchQuery search: The search query instance
        """

        search.query["bool"]["must_not"].append({"term": {"type": "composite"}})
        if not search.args.get("ignore_latest", False):
            search.query["bool"]["must_not"].append(
                {"constant_score": {"filter": {"exists": {"field": "nextversion"}}}}
            )

    def prefill_search_highlights(self, search, req):
        query_string = search.args.get("q")
        query_string_settings = app.config["ELASTICSEARCH_SETTINGS"]["settings"]["query_string"]
        advanced_search = json.loads(search.args.get("advanced")) if search.args.get("advanced") else {}

        field_settings = {"number_of_fragments": 0}
        if app.data.elastic.should_highlight(req) and (
            query_string or advanced_search.get("all") or advanced_search.get("any")
        ):
            elastic_highlight_query = get_elastic_highlight_query(
                query_string={
                    "query": query_string,
                    "default_operator": "AND",
                    "analyze_wildcard": query_string_settings["analyze_wildcard"],
                    "lenient": True,
                },
            )
            selected_field = advanced_search.get("fields") or []
            if not selected_field:
                elastic_highlight_query["fields"] = {
                    "body_html": field_settings,
                    "headline": field_settings,
                    "slugline": field_settings,
                }
            else:
                elastic_highlight_query["fields"] = {field: field_settings for field in selected_field}

            search.highlight = elastic_highlight_query

    def validate_request(self, search):
        """Validate the request parameters

        :param SearchQuery search: The search query instance
        """

        if not search.is_admin:
            if not search.company:
                abort(403, gettext("User does not belong to a company."))
            elif not len(search.products):
                abort(403, gettext("Your company doesn't have any products defined."))
            elif search.args.get("product") and not self.is_validate_product(search):
                abort(403, gettext("Your product is not assigned to you or your company."))
            # If a product list string has been provided it is assumed to be a comma delimited string of product id's
            elif search.args.get("requested_products"):
                # Ensure that all the provided products are permissioned for this request
                if not all(p in [c.get("_id") for c in search.products] for p in search.args["requested_products"]):
                    abort(404, gettext("Invalid product parameter"))

    def is_validate_product(self, data):
        """
        Check if the product is assigned to the user or to the company with zero or unlimited seats.

        :param SearchQuery data: The search query instance
        :return: True if the product is assigned to the user or to the company with zero or unlimited seats, False otherwise.
        :rtype: bool
        """
        user = data.user
        company = data.company
        product = data.args.get("product")

        if user and company and product:
            company_products_with_zero_seats = [p["_id"] for p in company.get("products", []) if not p.get("seats")]
            user_specific_products = [p["_id"] for p in user.get("products", [])]

            return ObjectId(product) in user_specific_products or ObjectId(product) in company_products_with_zero_seats

    def apply_section_filter(self, search, filters=None):
        """Generate the section filter

        :param SearchQuery search: the search query instance
        :param filters: list of section filters to use
        """
        return get_resource_service("section_filters").apply_section_filter(search.query, search.section, filters)

    def apply_company_filter(self, search):
        """Generate the company filter

        :param SearchQuery search: the search query instance
        """

        if search.is_admin or not search.company or not search.company.get("company_type"):
            return

        for company_type in app.config.get("COMPANY_TYPES", []):
            if company_type["id"] == search.company["company_type"]:
                if company_type.get("wire_must"):
                    search.query["bool"]["filter"].append(company_type["wire_must"])
                if company_type.get("wire_must_not"):
                    search.query["bool"]["must_not"].append(company_type["wire_must_not"])

    def apply_time_limit_filter(self, search):
        """Generate the time limit filter

        :param SearchQuery search: the search query instance
        """

        if search.is_admin:
            return

        limit_days = get_setting(self.limit_days_setting) if self.limit_days_setting is not None else None

        if limit_days and search.company and not search.company.get("archive_access", False):
            search.query["bool"]["filter"].append(
                {
                    "range": {
                        "versioncreated": {
                            "gte": "now-%dd/d" % int(limit_days),
                        }
                    }
                }
            )

    def apply_products_filter(self, search):
        """Generate the product filters

        :param SearchQuery search: the search query instance
        """

        if search.is_admin and not len(search.navigation_ids) and not search.args.get("product"):
            # admin will see everything by default
            return

        product_ids = [p["sd_product_id"] for p in search.products if p.get("sd_product_id")]

        if product_ids:
            search.query["bool"]["should"].append({"terms": {"products.code": product_ids}})

        for product in search.products:
            self.apply_product_filter(search, product)

    def apply_product_filter(self, search, product):
        """Generate the filter for a single product

        :param SearchQuery search: The search query instance
        :param dict product: The product to filter
        :return:
        """

        if search.args.get("requested_products") and product["_id"] not in search.args["requested_products"]:
            return

        if product.get("query"):
            search.query["bool"]["should"].append(query_string(product["query"]))

    def apply_request_filter(self, search):
        if search.args.get("q"):
            search.query["bool"]["filter"].append(
                query_string(search.args["q"], search.args.get("default_operator") or "AND")
            )

        filters = None
        if search.args.get("filter"):
            if isinstance(search.args["filter"], dict):
                filters = search.args["filter"]
            else:
                try:
                    filters = json.loads(search.args["filter"])
                except TypeError:
                    raise BadParameterValueError("Incorrect type supplied for filter parameter")

        if not app.config.get("FILTER_BY_POST_FILTER", False):
            if filters:
                if app.config.get("FILTER_AGGREGATIONS", True):
                    self.set_bool_query_from_filters(search.query["bool"], filters)
                else:
                    search.query["bool"]["filter"].append(filters)

            if search.args.get("created_from") or search.args.get("created_to"):
                search.query["bool"]["filter"].append(self.versioncreated_range(search.args))
        elif filters or search.args.get("created_from") or search.args.get("created_to"):
            search.source["post_filter"] = {"bool": {"filter": []}}

            if filters:
                if app.config.get("FILTER_AGGREGATIONS", True):
                    self.set_bool_query_from_filters(search.source["post_filter"]["bool"], filters)
                else:
                    search.source["post_filter"]["bool"]["filter"].append(filters)

            if search.args.get("created_from") or search.args.get("created_to"):
                search.source["post_filter"]["bool"]["filter"].append(self.versioncreated_range(search.args))

    def apply_request_advanced_search(self, search: SearchQuery):
        if not search.args.get("advanced"):
            return

        if isinstance(search.args["advanced"], str):
            search.advanced = json.loads(search.args["advanced"])
        else:
            search.advanced = search.args["advanced"]

        fields = search.advanced.get("fields") or self.default_advanced_search_fields
        if not fields:
            return

        def gen_match_query(keywords: str, operator: str, multi_match_type):
            return {
                "multi_match": {
                    "query": keywords,
                    "type": multi_match_type,
                    "fields": fields,
                    "operator": operator,
                },
            }

        if search.advanced.get("all"):
            search.query["bool"]["filter"].append(gen_match_query(search.advanced["all"], "AND", "cross_fields"))
        if search.advanced.get("any"):
            search.query["bool"]["filter"].append(gen_match_query(search.advanced["any"], "OR", "best_fields"))
        if search.advanced.get("exclude"):
            search.query["bool"]["must_not"].append(gen_match_query(search.advanced["exclude"], "OR", "best_fields"))

    def apply_embargoed_filters(self, search):
        """Generate filters for embargoed params"""

        if search.args.get("exclude_embargoed"):
            search.query["bool"]["must_not"].append({"range": {"embargoed": {"gt": "now"}}})
        elif search.args.get("embargoed_only"):
            search.query["bool"]["filter"].append({"range": {"embargoed": {"gt": "now"}}})

    def prepend_embargoed_items_to_response(self, response, req, lookup):
        search = SearchQuery()
        self.prefill_search_args(search, req)
        search.args.update(
            {
                "exclude_embargoed": False,
                "embargoed_only": True,
            }
        )

        self.prefill_search_query(search, req, lookup)
        self.apply_filters(search)
        self.gen_source_from_search(search)
        internal_req = self.get_internal_request(search)
        embargoed_response = self.internal_get(internal_req, search.lookup)

        if embargoed_response.count():
            response.docs = embargoed_response.docs + response.docs
            response.hits["hits"]["total"] = response.count() + embargoed_response.count()

    def get_matching_topics_for_item(self, topics, users, companies, query):
        aggs = {"topics": {"filters": {"filters": {}}}}

        queried_topics = []
        # get all section filters
        section_filters = get_resource_service("section_filters").get_section_filters_dict()

        for topic in topics:
            search = SearchQuery()

            user = users.get(str(topic["user"]))
            if not user:
                continue

            search.user = user
            search.is_admin = is_admin(user)
            search.company = companies.get(str(user.get("company", "")))

            search.query = deepcopy(query)
            search.section = topic.get("topic_type")

            self.prefill_search_products(search)

            if topic.get("query"):
                search.query["bool"]["filter"].append(query_string(topic["query"]))

            if topic.get("created"):
                search.query["bool"]["filter"].append(
                    self.versioncreated_range(
                        dict(
                            created_from=topic["created"].get("from"),
                            created_to=topic["created"].get("to"),
                            timezone_offset=topic.get("timezone_offset", "0"),
                        )
                    )
                )

            if topic.get("filter"):
                self.set_bool_query_from_filters(search.query["bool"], topic["filter"])

            if topic.get("advanced"):
                search.args["advanced"] = topic["advanced"]

            # for now even if there's no active company matching for the user
            # continuing with the search
            try:
                self.validate_request(search)
                self.apply_section_filter(search, section_filters)
                self.apply_company_filter(search)
                self.apply_time_limit_filter(search)
                self.apply_products_filter(search)
                self.apply_request_advanced_search(search)
            except Forbidden as exc:
                logger.info(
                    "Notification for user:{} and topic:{} is skipped".format(user.get("_id"), topic.get("_id")),
                    exc_info=exc,
                )
                continue

            aggs["topics"]["filters"]["filters"][str(topic["_id"])] = search.query

            queried_topics.append(topic)

        source = {"query": query}
        source["aggs"] = aggs if aggs["topics"]["filters"]["filters"] else {}
        source["size"] = 0

        req = ParsedRequest()
        req.args = {"source": json.dumps(source)}
        topic_matches = []

        try:
            search_results = self.internal_get(req, None)

            for topic in queried_topics:
                if search_results.hits["aggregations"]["topics"]["buckets"][str(topic["_id"])]["doc_count"] > 0:
                    topic_matches.append(topic["_id"])

        except Exception as exc:
            logger.error(
                "Error in get_matching_topics for query: {}".format(json.dumps(source)),
                exc,
                exc_info=True,
            )
            raise

        return topic_matches
