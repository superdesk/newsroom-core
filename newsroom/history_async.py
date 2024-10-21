from typing import Any, cast

import pymongo.errors
from bson import ObjectId
import werkzeug.exceptions
from quart_babel import gettext

from superdesk.core.types import Request, Response
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

from newsroom.types import HistoryResourceModel
from newsroom.core.resources.service import NewshubAsyncResourceService
from newsroom import MONGO_PREFIX, ELASTIC_PREFIX
from newsroom.auth.utils import get_user_from_request
from newsroom.utils import get_json_or_400


class HistoryService(NewshubAsyncResourceService[HistoryResourceModel]):
    async def create_history_record(
        self,
        docs: list[dict[str, Any]],
        action: str,
        user_id: ObjectId | None,
        company_id: ObjectId | None,
        section: str = "wire",
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


async def get_history_users(
    item_ids: list[ObjectId | str],
    active_user_ids: list[ObjectId | str],
    active_company_ids: list[ObjectId | str],
    section: str,
    action: str,
) -> list[str]:
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

    histories_cursor = await HistoryService().find(source)

    # Collect the history items
    histories_items = []
    async for history in histories_cursor:
        histories_items.append(history)

    # Filter out the users
    user_ids = [str(uid) for uid in active_user_ids]
    return [str(h["user"]) for h in histories_items if str(h["user"]) in user_ids]


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


module = Module(
    name="newsroom.history_async",
    resources=[history_resource_config],
    endpoints=[history_endpoint],
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
