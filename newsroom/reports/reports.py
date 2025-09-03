from typing import cast
from collections import defaultdict
from copy import deepcopy

from bson import ObjectId
from quart_babel import gettext
from superdesk import get_app_config

from superdesk.core import get_current_app
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync, ResourceCursorAsync
from superdesk.flask import abort, request
from superdesk.utc import utcnow, utc_to_local, get_date

from newsroom.types import CompanyResource, NewsApiAuditResourceModel, AgendaItem, WireItem
from newsroom.history_async import HistoryService
from newsroom.auth.utils import get_company_from_request
from newsroom.utils import (
    query_resource,
    get_entity_dict,
    MAX_TERMS_SIZE,
)
from newsroom.companies.companies_async import CompanyService
from newsroom.search.types import BaseSearchRequestArgs
from newsroom.agenda.filters import get_date_filters
from newsroom.news_api.api_tokens import API_TOKENS
from newsroom.news_api.utils import format_report_results
from newsroom.companies.utils import get_companies_id_by_product
from newsroom.topics.topics_async import TopicService
from newsroom.companies import CompanyServiceAsync
from newsroom.users.service import UsersService
from newsroom.products.service import ProductsService
from newsroom.wire import WireSearchServiceAsync, WireSearchRequestArgs
from newsroom.agenda.agenda_service import AgendaItemService
from .content_activity import get_content_activity_report  # noqa


async def get_company_saved_searches():
    """Returns number of saved searches by company"""
    results = []
    company_topics = defaultdict(int)
    companies = get_entity_dict(await CompanyServiceAsync().get_all_raw_as_list())
    users = get_entity_dict(await UsersService().get_all_raw_as_list())

    topics = await TopicService().get_all_raw_as_list()

    for topic in topics:
        company = users.get(topic.get("user", ""), {}).get("company")
        if company:
            company_topics[company] += 1

    for _id, topic_count in company_topics.items():
        results.append(
            {
                "_id": _id,
                "name": companies.get(_id, {}).get("name"),
                "is_enabled": companies.get(_id, {}).get("is_enabled"),
                "topic_count": topic_count,
            }
        )

    sorted_results = sorted(results, key=lambda k: k["name"])
    return {"results": sorted_results, "name": gettext("Saved searches per company")}


async def get_user_saved_searches():
    """Returns number of saved searches by user"""
    results = []
    user_topics = defaultdict(int)
    companies = get_entity_dict(await CompanyServiceAsync().get_all_raw_as_list())
    users = get_entity_dict(await UsersService().get_all_raw_as_list())

    topics = await TopicService().get_all_raw_as_list()

    for topic in topics:
        company = users.get(topic.get("user", ""), {}).get("company")
        if company:
            user_topics[topic["user"]] += 1

    for _id, topic_count in user_topics.items():
        results.append(
            {
                "_id": _id,
                "name": "{} {}".format(
                    users.get(_id, {}).get("first_name"),
                    users.get(_id, {}).get("last_name"),
                ),
                "is_enabled": users.get(_id, {}).get("is_enabled"),
                "company": companies.get(users.get(_id, {}).get("company", ""), {}).get("name"),
                "topic_count": topic_count,
            }
        )

    sorted_results = sorted(results, key=lambda k: k["name"])
    return {"results": sorted_results, "name": gettext("Saved searches per user")}


async def get_company_and_user_saved_searches():
    """
    Returns saved My topics and Company topics per user in their company
    """

    results = []
    current_company = get_company_from_request(None)
    lookup_company = dict(company=current_company.id if current_company else None)

    users_cursor = await UsersService().find(lookup_company)
    users = get_entity_dict(await users_cursor.to_list_raw())

    cursor = await TopicService().find(lookup_company)
    topics = await cursor.to_list_raw()

    saved_topics = defaultdict(lambda: dict(my_topics=0, company_topics=0))

    for topic in topics:
        topics_key = "company_topics" if topic.get("is_global") else "my_topics"
        saved_topics[topic["user"]][topics_key] += 1

    for _id, topics_count in saved_topics.items():
        results.append(
            {
                "_id": _id,
                "name": "{} {}".format(
                    users.get(_id, {}).get("first_name"),
                    users.get(_id, {}).get("last_name"),
                ),
                "is_enabled": users.get(_id, {}).get("is_enabled"),
                "my_topics_count": topics_count.get("my_topics"),
                "company_topics_count": topics_count.get("company_topics"),
            }
        )

    sorted_results = sorted(results, key=lambda k: k["name"])
    return {"results": sorted_results, "name": gettext("Saved My Topics and Company Topics")}


async def get_company_products():
    """Returns products by company"""
    results = []
    companies = get_entity_dict(await CompanyServiceAsync().get_all_raw_as_list())
    products_data = get_entity_dict(await ProductsService().get_all_raw_as_list())
    for company_id, company_details in companies.items():
        company_result = {
            "_id": str(company_id),
            "name": company_details.get("name", ""),
            "is_enabled": company_details.get("is_enabled", ""),
            "products": [
                products_data.get(product_info.get("_id")) for product_info in company_details.get("products", [])
            ],
        }
        results.append(company_result)

    sorted_results = sorted(results, key=lambda k: k["name"])
    return {"results": sorted_results, "name": gettext("Products per company")}


async def get_product_stories():
    """Returns the story count per product for today, this week, this month ..."""

    results = []

    async for product in ProductsService().get_all():
        product_stories = {
            "_id": product.id,
            "name": product.name,
            "is_enabled": product.is_enabled,
        }
        counts = await WireSearchServiceAsync().get_product_item_report(product)
        for key, value in counts.hits["aggregations"].items():
            product_stories[key] = value["buckets"][0]["doc_count"]

        results.append(product_stories)

    sorted_results = sorted(results, key=lambda k: k["name"])
    return {"results": sorted_results, "name": gettext("Stories per product")}


async def get_company_report():
    """Returns products by company"""
    results = []
    companies = await CompanyServiceAsync().get_all_raw_as_list()
    products_data = get_entity_dict(await ProductsService().get_all_raw_as_list())
    users_service = UsersService()

    for company in companies:
        company_id = str(company["_id"])
        cursor = await users_service.find({"company": company_id})
        users = await cursor.to_list_raw()

        company_result = {
            "_id": company_id,
            "name": company["name"],
            "is_enabled": company["is_enabled"],
            "products": [products_data.get(prod.get("_id")) for prod in company.get("products", [])],
            "users": users,
            "company": company_id,
            "account_manager": company.get("account_manager"),
        }
        results.append(company_result)

    sorted_results = sorted(results, key=lambda k: k["name"])
    return {"results": sorted_results, "name": gettext("Company")}


async def get_subscriber_activity_report():
    args = deepcopy(request.args.to_dict())

    # Elastic query
    must_terms = []
    source = {}

    if args.get("company"):
        must_terms.append({"term": {"company": args.get("company")}})

    if args.get("action"):
        must_terms.append({"term": {"action": args.get("action")}})

    if args.get("section"):
        must_terms.append({"term": {"section": args.get("section")}})

    date_range = get_date_filters(
        BaseSearchRequestArgs(
            start_date=args["date_from"],
            end_date=args["date_to"],
            timezone_offset=args.get("timezone_offset"),
        )
    )
    if date_range.get("gt") or date_range.get("lt"):
        must_terms.append({"range": {"versioncreated": date_range}})

    source["sort"] = [{"versioncreated": "desc"}]
    if len(must_terms) > 0:
        source["query"] = {"bool": {"filter": must_terms}}

    source["size"] = 25
    source["from"] = int(args.get("from", 0))

    if source["from"] >= 5000:
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/pagination.html#pagination
        return abort(400)

    history_cursor = await HistoryService().search(source)
    docs = await history_cursor.to_list_raw()
    if args.get("export", "").lower() == "true":
        while True:
            source["from"] = len(docs)
            history_cursor = await HistoryService().search(source)
            next_items = await history_cursor.to_list_raw()
            if next_items:
                docs.extend(next_items)
            else:
                break

    # Enhance the results
    wire_ids = []
    agenda_ids = []
    company_ids = []
    user_ids = []
    for doc in docs:
        if doc.get("section") == "agenda":
            agenda_ids.append(doc.get("item"))
        else:
            wire_ids.append(doc.get("item"))

        if doc.get("company"):
            company_ids.append(ObjectId(doc.get("company")))
        user_ids.append(ObjectId(doc.get("user")))
    # remove duplicates for efficiency
    wire_ids = list(set(wire_ids))
    agenda_ids = list(set(agenda_ids))

    AGENDAITEM_CHUNK_SIZE: int = 100
    agenda_items: dict[str, AgendaItem] = {}
    for i in range(0, len(agenda_ids), AGENDAITEM_CHUNK_SIZE):
        agenda_cursor: ResourceCursorAsync[AgendaItem] = await AgendaItemService().search(
            {"_id": {"$in": agenda_ids[i : i + AGENDAITEM_CHUNK_SIZE]}}, use_mongo=True
        )
        agenda_items.update({agenda_item.id: agenda_item async for agenda_item in agenda_cursor})

    # request the wire_items in chunks, in the case of export the list may be quite long
    WIREITEM_CHUNK_SIZE: int = 100
    wire_items: dict[str, WireItem] = {}
    args = WireSearchRequestArgs(ignore_latest=True)
    args.page_size = WIREITEM_CHUNK_SIZE
    for i in range(0, len(wire_ids), WIREITEM_CHUNK_SIZE):
        wire_cursor: ElasticsearchResourceCursorAsync[WireItem] = await WireSearchServiceAsync().get_items_by_id(
            wire_ids[i : i + WIREITEM_CHUNK_SIZE], args=args
        )
        wire_items.update({wire_item.id: wire_item async for wire_item in wire_cursor})

    company_items = {
        str(company.id): company for company in await CompanyService().find_items_by_ids(list(set(company_ids)))
    }
    user_items = {str(user.id): user for user in await UsersService().find_items_by_ids(list(set(user_ids)))}

    def get_section_name(s):
        return next((sec for sec in get_current_app().as_any().sections if sec.get("_id") == s), {}).get("name")

    for doc in docs:
        if doc.get("item") in wire_items:
            item_data = wire_items[doc["item"]]
            doc["item"] = {
                "item_text": item_data.headline,
                "_id": item_data.id,
                "item_href": "/{}?item={}".format(
                    doc["section"] if doc["section"] != "news_api" else "wire",
                    doc["item"],
                ),
                "published": item_data.versioncreated,
                "place": "\r\n".join([_p.name or "" for _p in item_data.place or []]),
                "service": "\r\n".join([_s.name or "" for _s in item_data.service or []]),
                "subject": "\r\n".join([_s.name or "" for _s in item_data.subject or []]),
                "anpa_take_key": item_data.anpa_take_key,
                "slugline": item_data.slugline,
            }
            try:
                if "download" in doc.get("action", "") and doc.get("extra_data") is not None:
                    wire_item = wire_items.get(doc.get("item", {}).get("_id"))
                    if wire_item:
                        association_key = doc.get("extra_data", {}).get("association")
                        association_detail = wire_item.associations.get(association_key, {})
                        association_value = (
                            gettext("Feature")
                            if association_key == "featuremedia"
                            else gettext("Embedded")
                            if association_key and association_key.startswith("editor_")
                            else ""
                        )
                        guid_value = association_detail.get("guid", "")
                        doc["association"] = {
                            "text": association_detail.get("headline", "N/A"),
                            "href": "/assets/{}".format(
                                association_detail.get("renditions", {}).get("original", {}).get("media", "")
                            ),
                            "type": association_detail.get("type"),  # get() here if type might be missing
                            "reference": f"{association_value}:{guid_value}" if association_value or guid_value else "",
                        }
            except Exception:
                pass
        elif doc.get("item") in agenda_items:
            item_data = agenda_items[doc["item"]]
            doc["item"] = {
                "item_text": item_data.name or item_data.headline or item_data.slugline,
                "_id": item_data.id,
                "item_href": "/agenda?item={}".format(doc["item"]),  # doc["item"] is the original ID
                "place": "\r\n".join([_p.name or "" for _p in item_data.place or []]),
                "service": "\r\n".join([_s.name or "" for _s in item_data.service or []]),
                "subject": "\r\n".join([_s.name or "" for _s in item_data.subject or []]),
                "published": item_data.versioncreated,
            }

        if doc.get("company") in company_items:
            doc["company"] = company_items[doc.get("company")].name

        if doc.get("user") in user_items:
            user = user_items[doc.get("user")]
            doc["user"] = "{0} {1}".format(user.first_name, user.last_name)

        doc["section"] = get_section_name(doc["section"])
        doc["action"] = doc["action"].capitalize() if doc["action"].lower() != "api" else "API retrieval"

    if not request.args.get("export"):
        results = {
            "results": docs,
            "name": gettext("SubscriberActivity"),
        }
        return results
    else:
        field_names = [
            "Company",
            "Section",
            "Item",
            "Action",
            "User",
            "Published",
            "Place",
            "Slugline",
            "Takekey",
            "Category",
            "Subject",
            "Reference",
            "Created",
        ]
        rows = []
        rows.append(field_names)
        for doc in docs:
            item_value = doc.get("item")
            row = [
                doc.get("company", "") or "",
                doc.get("section", "") or "",
                item_value.get("item_text", "") if isinstance(item_value, dict) else (item_value or ""),
                doc.get("action", "") or "",
                doc.get("user", "N/A") or "",
                utc_to_local(get_app_config("DEFAULT_TIMEZONE"), item_value.get("published")).strftime("%H:%M %d/%m/%y")
                if isinstance(item_value, dict) and item_value.get("published")
                else "",
                item_value.get("place") or "" if isinstance(item_value, dict) else "",
                item_value.get("slugline") or "" if isinstance(item_value, dict) else "",
                item_value.get("anpa_take_key") or "" if isinstance(item_value, dict) else "",
                item_value.get("service") or "" if isinstance(item_value, dict) else "",
                item_value.get("subject") or "" if isinstance(item_value, dict) else "",
                doc.get("association", {}).get("reference", "") or "",
                utc_to_local(get_app_config("DEFAULT_TIMEZONE"), get_date(doc.get("versioncreated"))).strftime(
                    "%H:%M %d/%m/%y"
                ),
            ]
            rows.append(row)
        return rows


async def get_company_api_usage():
    args = deepcopy(request.args.to_dict())
    date_range = get_date_filters(
        BaseSearchRequestArgs(
            start_date=args["date_from"],
            end_date=args["date_to"],
            timezone_offset=args.get("timezone_offset"),
        )
    )

    if not date_range.get("gt") and date_range.get("lt"):
        abort(400, "No date range specified.")

    page_from = int(args.get("from", 0))
    if page_from >= 1000:
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/pagination.html#pagination
        return abort(400)

    # TODO-ASYNC: Change this when CompanyTokenAuth is upgraded to async
    company_ids = [t["company"] for t in query_resource(API_TOKENS)]
    companies = {str(company.id): company for company in await CompanyResource.get_service().find_by_ids(company_ids)}

    cursor = cast(
        ElasticsearchResourceCursorAsync[NewsApiAuditResourceModel],
        await NewsApiAuditResourceModel.get_service().search(
            {
                "query": {
                    "bool": {
                        "filter": [
                            {"range": {"created": date_range}},
                            {"terms": {"subscriber": company_ids}},
                        ],
                    },
                },
                "sort": [{"created": "desc"}],
                "size": 200,
                "from": page_from,
                "aggs": {
                    "items": {
                        "aggs": {"endpoints": {"terms": {"size": MAX_TERMS_SIZE, "field": "endpoint.keyword"}}},
                        "terms": {"size": MAX_TERMS_SIZE, "field": "subscriber.keyword"},
                    },
                },
            }
        ),
    )

    unique_endpoints = []
    results = format_report_results(cursor, unique_endpoints, companies)

    results = {
        "results": results,
        "name": gettext("Company News API Usage"),
        "result_headers": unique_endpoints,
    }
    return results


async def get_company_names(company_ids):
    service_async = CompanyServiceAsync()
    enabled_companies = []
    disabled_companies = []
    for company_id in company_ids:
        company = await service_async.find_by_id_raw(company_id)
        if company:
            if not company.get("is_enabled"):
                disabled_companies.append(company.get("name"))
            else:
                enabled_companies.append(company.get("name"))
    return {
        "enabled_companies": enabled_companies,
        "disabled_companies": disabled_companies,
    }


async def get_product_company():
    args = deepcopy(request.args.to_dict())
    lookup = {"_id": ObjectId(args.get("product"))} if args.get("product") else None
    cursor = await ProductsService().find(lookup)
    products = await cursor.to_list_raw()

    res = [
        {
            "_id": product.get("_id"),
            "product": product.get("name"),
            "companies": await get_companies_id_by_product(product.get("_id")),
        }
        for product in products
    ]

    for r in res:
        r.update(await get_company_names(r.get("companies", [])))

    results = {"results": res, "name": gettext("Companies permissioned per product")}
    return results


async def get_expired_companies():
    lookup = {"expiry_date": {"$lte": utcnow().replace(hour=0, minute=0, second=0)}}
    cursor = await CompanyServiceAsync().find(lookup)
    expired = await cursor.to_list_raw()

    results = {"results": expired, "name": gettext("Expired companies")}
    return results
