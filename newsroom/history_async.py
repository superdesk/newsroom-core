import pymongo.errors
from bson import ObjectId
import werkzeug.exceptions

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Annotated, List, Any

from newsroom import MONGO_PREFIX, ELASTIC_PREFIX
from newsroom.users.utils import get_user_or_abort
from newsroom.utils import get_json_or_400
from newsroom.core.resources.model import NewshubResourceModel
from newsroom.core.resources.service import NewshubAsyncResourceService
from newsroom.users.model import UserResourceModel

from superdesk.core.module import Module
from quart_babel import gettext
from superdesk.utc import utcnow
from superdesk.core.web import EndpointGroup, Response, Request
from superdesk.flask import abort
from superdesk.core.resources.fields import ObjectId as ObjectIdField, Keyword
from superdesk.core.resources.validators import validate_data_relation_async
from superdesk.core.resources import (
    ResourceConfig,
    MongoResourceConfig,
    MongoIndexOptions,
    ElasticResourceConfig,
)


class RouteParams(BaseModel):
    item: Optional[Dict[str, Any]] = None
    action: Optional[str] = None
    section: Optional[str] = None


class HistoryResourceModel(NewshubResourceModel):
    action: Keyword
    versioncreated: datetime
    user: Optional[Annotated[ObjectIdField, validate_data_relation_async("users")]] = None
    company: Optional[Annotated[ObjectIdField, validate_data_relation_async("companies")]] = None
    item: Keyword
    version: str
    section: Keyword
    extra_data: Optional[Dict] = None


class HistoryService(NewshubAsyncResourceService[HistoryResourceModel]):
    async def create_history_record(
        self, docs: List[Dict[str, Any]], action: str, user: UserResourceModel, section: str = "wire", **kwargs: Any
    ):
        now = utcnow()

        def transform(item: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "action": action,
                "versioncreated": now,
                "user": user["_id"],
                "company": user.get("company"),
                "item": str(item["_id"]),
                "version": str(item.get("version", item.get("_current_version"))),
                "section": section,
            }

        transformed_docs = [transform(doc) for doc in docs]
        try:
            await super().create(transformed_docs)
        except (werkzeug.exceptions.Conflict, pymongo.errors.BulkWriteError):
            pass

    async def query_items(self, query: Dict[str, Any]):
        if query["from"] >= 1000:
            # https://www.elastic.co/guide/en/elasticsearch/guide/current/pagination.html#pagination
            abort(400)

        # Use self.find to execute the query and get the cursor
        cursor = await self.find(query)
        return cursor

    async def fetch_history(self, query: Dict[str, Any], all: bool = False):
        cursor = await self.query_items(query)

        # Fetch the documents from the cursor
        docs = []
        async for doc in cursor:
            docs.append(doc)

        if all:
            # Handle pagination and retrieve additional results
            while cursor.hits["hits"]["total"]["value"] > len(docs):
                query["from"] = len(docs)
                cursor = await self.query_items(query)
                async for doc in cursor:
                    docs.append(doc)

        # Return the results
        return {"_items": docs, "hits": cursor.hits}


async def get_history_users(
    item_ids: list[ObjectId | str],
    active_user_ids: list[ObjectId | str],
    active_company_ids: list[ObjectId | str],
    section: str,
    action: str,
) -> List[str]:
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
                name="item",
                keys=[("item", 1)],
            ),
            MongoIndexOptions(
                name="company_user",
                keys=[("company", 1), ("user", 1)],
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
async def create(args: None, params: RouteParams, request: Request) -> Response:
    params_dict = await get_json_or_400()
    user = await get_user_or_abort()

    if not params_dict.get("item") or not params_dict.get("action") or not params_dict.get("section"):
        return Response({"error": str(gettext("Activity History: Invalid request"))}, 400)

    await HistoryService().create_history_record(
        [params_dict["item"]], params_dict["action"], user.to_dict(), params_dict["section"]
    )

    return Response({"success": True}, 201)
