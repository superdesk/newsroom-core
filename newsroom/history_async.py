from typing import Any, cast

import pymongo.errors
from bson import ObjectId
import werkzeug.exceptions
from quart_babel import gettext
import logging

from superdesk.core.types import Request, Response
from superdesk.core.app import SuperdeskAsyncApp
from superdesk.core.module import Module
from superdesk.core.resources import (
    ResourceConfig,
    MongoResourceConfig,
    MongoIndexOptions,
    ElasticResourceConfig,
)
from superdesk.core.resources.cursor import ElasticsearchResourceCursorAsync
from superdesk.core.web import EndpointGroup
from superdesk.utc import utcnow
from superdesk.flask import abort

from newsroom.types import HistoryResourceModel, UserResourceModel, SectionEnum, WireItem
from newsroom.core import NewshubModuleConfig
from newsroom.auth.utils import get_company_or_none_from_request
from newsroom.core.resources.service import NewshubAsyncResourceService
from newsroom import MONGO_PREFIX, ELASTIC_PREFIX
from newsroom.auth.utils import get_user_from_request
from newsroom.utils import get_json_or_400

logger = logging.getLogger(__name__)


class HistoryService(NewshubAsyncResourceService[HistoryResourceModel]):
    async def create_history_record(
        self,
        docs: list[dict[str, Any]],
        action: str,
        user_id: ObjectId | None,
        company_id: ObjectId | None,
        section: str = "wire",
        monitoring_id: ObjectId | None = None,
    ):
        now = utcnow()

        def transform(item: dict[str, Any]) -> dict[str, Any]:
            return {
                "action": action,
                "versioncreated": now,
                "user": user_id,
                "company": company_id,
                "item": str(item["_id"]),
                "version": str(item.get("version", item.get("_current_version"))),
                "section": section,
                "monitoring": monitoring_id,
            }

        transformed_docs = [transform(doc) for doc in docs]
        try:
            await super().create(transformed_docs)
        except (werkzeug.exceptions.Conflict, pymongo.errors.BulkWriteError):
            pass

    async def query_items(self, query: dict[str, Any]) -> ElasticsearchResourceCursorAsync[HistoryResourceModel]:
        if query["from"] >= 1000:
            # https://www.elastic.co/guide/en/elasticsearch/guide/current/pagination.html#pagination
            abort(400)

        # Use self.find to execute the query and get the cursor
        return cast(ElasticsearchResourceCursorAsync, await self.find(query))

    async def fetch_history(self, query: dict[str, Any], all: bool = False):
        cursor = await self.query_items(query)

        # Fetch the documents from the cursor
        docs = await cursor.to_list_raw()

        if all:
            # Handle pagination and retrieve additional results
            while await cursor.count() > len(docs):
                query["from"] = len(docs)
                cursor = await self.query_items(query)
                docs.extend(await cursor.to_list_raw())

        # Return the results
        return {"_items": docs, "hits": cursor.hits}

    async def create_media_history_record(
        self, item: dict[str, Any], association_name: str, action: str | None, user: UserResourceModel, section: str
    ):
        """
        Log the download of an association belonging to an item
        :param item:
        :param association_name:
        :param action:
        :param user:
        :param section:
        :return:
        """
        now = utcnow()
        if action is None:
            action = "media"
        entry = {
            "action": action,
            "versioncreated": now,
            "user": user.id,
            "company": user.company,
            "item": item.get("_id"),
            "version": item.get("version") if item.get("version") else item.get("_current_version", ""),
            "section": section,
            "extra_data": {"association": association_name},
        }
        try:
            await super().create([entry])
        except (werkzeug.exceptions.Conflict, pymongo.errors.BulkWriteError):
            pass

    async def log_api_media_download(self, item_id: str | None, media_id: str):
        """
        Given am item, media reference and a user record the download
        :param item_id:
        :param media_id:
        :return:
        """
        if not item_id:
            return

        item = await WireItem.get_service().find_by_id_raw(item_id)
        if not item:
            logger.warning(f"Failed find item to log api media download for {item_id} with media id {media_id}")
            abort(404)

        # Find the matching media in the item
        media_name: str | None = None
        media_item: dict | None = None
        for name, association in (item.get("associations") or {}).items():
            for rendition in item.get("associations", {}).get(name).get("renditions", {}):
                if association.get("renditions", {}).get(rendition).get("media", "") == media_id:
                    media_name = name
                    media_item = association
                    break
            if media_item is not None:
                break

        if not media_item or not media_name:
            logger.warning(f"Failed find rendition to log api media download for {item_id} with media id {media_id}")
            abort(404)

        company = get_company_or_none_from_request(None)
        if not company:
            logger.warning("Failed to find company to log api media download")

        action = "download " + media_item.get("type", "")  # type: ignore
        entry = {
            "action": action,
            "versioncreated": utcnow(),
            "company": company.id if company else None,
            "item": item.get("_id"),
            "version": item.get("version") if item.get("version") else item.get("_current_version", ""),
            "section": SectionEnum.NEWS_API.value,
            "extra_data": {"association": media_name},
        }
        try:
            await super().create([entry])
        except (werkzeug.exceptions.Conflict, pymongo.errors.BulkWriteError):
            logger.warning(f"Failed to write to mongo to log api media download for {item_id} with media id {media_id}")
            pass


async def get_history_users(
    item_ids: list[str],
    active_user_ids: list[ObjectId],
    active_company_ids: list[ObjectId],
    section: str,
    action: str,
) -> set[ObjectId]:
    source = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "bool": {
                            "should": [
                                {"terms": {"company": [str(a) for a in active_company_ids]}},
                                {"bool": {"must_not": [{"exists": {"field": "company"}}]}},
                            ],
                            "minimum_should_match": 1,
                        },
                    },
                    {"terms": {"item": [str(i) for i in item_ids]}},
                    {"term": {"section": section}},
                    {"term": {"action": action}},
                ]
            }
        },
        "size": 25,
        "from": 0,
    }

    histories_cursor = await HistoryService().search(source)

    # Return list of active user IDs who have an action on these items
    return set([history.user async for history in histories_cursor if history.user in active_user_ids])


history_resource_config = ResourceConfig(
    name="history",
    data_class=HistoryResourceModel,
    service=HistoryService,
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
        indexes=[
            MongoIndexOptions(
                name="company_user",
                keys=[("item", 1), ("company", 1), ("user", 1)],
                unique=False,
            ),
        ],
    ),
    elastic=ElasticResourceConfig(prefix=ELASTIC_PREFIX),
)

history_endpoint = EndpointGroup("history", __name__)


def init_module(app: SuperdeskAsyncApp):
    if history_config.register_endpoints:
        app.wsgi.register_endpoint(history_endpoint)


history_config = NewshubModuleConfig()
module = Module(
    name="newsroom.history_async",
    config=history_config,
    resources=[history_resource_config],
    endpoints=[],
    init=init_module,
)


@history_endpoint.endpoint("/history/new", methods=["POST"])
async def create(request: Request) -> Response:
    params_dict = await get_json_or_400()
    user = get_user_from_request(request)

    if not params_dict.get("item") or not params_dict.get("action") or not params_dict.get("section"):
        return Response({"error": gettext("Activity History: Invalid request")}, 400)

    await HistoryService().create_history_record(
        [params_dict["item"]],
        params_dict["action"],
        user.id,
        user.company,
        params_dict["section"],
    )

    return Response({"success": True}, 201)
