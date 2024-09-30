import pymongo.errors
import werkzeug.exceptions

from superdesk import get_resource_service
from superdesk.resource import not_analyzed, not_enabled
from superdesk.utc import utcnow
from quart_babel import gettext
from eve.utils import ParsedRequest

from superdesk.core import json
from superdesk.flask import abort, Blueprint, jsonify
import newsroom
from newsroom.utils import get_json_or_400
from newsroom.auth import get_user

blueprint = Blueprint("history", __name__)

# TODO-ASYNC :- Remove this resource when Reports module is converted to async


class HistoryResource(newsroom.Resource):
    item_methods = ["GET"]
    resource_methods = ["GET"]

    schema = {
        "_id": {"type": "string", "unique": True},
        "action": {"type": "string", "mapping": not_analyzed},
        "versioncreated": {"type": "datetime"},
        "user": newsroom.Resource.rel("users"),
        "company": newsroom.Resource.rel("companies"),
        "item": {"type": "string", "mapping": not_analyzed},
        "version": {"type": "string"},
        "section": {"type": "string", "mapping": not_analyzed},
        "extra_data": {"type": "object", "mapping": not_enabled},
    }

    mongo_indexes: newsroom.MongoIndexes = {
        "item": ([("item", 1)], {}),
        "company_user": ([("company", 1), ("user", 1)], {}),
    }

    datasource = {"source": "history", "search_backend": "elastic"}


class HistoryService(newsroom.Service):
    def create(self, docs, action, user, section="wire", **kwargs):
        now = utcnow()

        def transform(item):
            return {
                "action": action,
                "versioncreated": now,
                "user": user["_id"],
                "company": user.get("company"),
                "item": item["_id"],
                "version": item.get("version", item.get("_current_version")),
                "section": section,
            }

        for doc in docs:
            try:
                super().create([transform(doc)])
            except (werkzeug.exceptions.Conflict, pymongo.errors.BulkWriteError):
                continue

    def create_history_record(self, items, action, user, section):
        self.create(items, action, user, section)

    def query_items(self, query):
        if query["from"] >= 1000:
            # https://www.elastic.co/guide/en/elasticsearch/guide/current/pagination.html#pagination
            return abort(400)

        req = ParsedRequest()
        req.args = {"source": json.dumps(query)}
        return super().get(req, None)

    def fetch_history(self, query, all=False):
        results = self.query_items(query)
        docs = results.docs
        if all:
            while results.hits["hits"]["total"]["value"] > len(docs):
                query["from"] = len(docs)
                results = self.query_items(query)
                docs.extend(results.docs)

        return {"items": docs, "hits": results.hits}


def get_history_users(item_ids, active_user_ids, active_company_ids, section, action):
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

    # Get the results
    histories = get_resource_service("history").fetch_history(source, all=True).get("items") or []

    # Filter out the users
    user_ids = [str(uid) for uid in active_user_ids]
    return [str(h["user"]) for h in histories if h.get("user") in user_ids]


@blueprint.route("/history/new", methods=["POST"])
async def create():
    params = await get_json_or_400()
    if not params.get("item") or not params.get("action") or not params.get("section"):
        return "", gettext("Activity History: Inavlid request")

    get_resource_service("history").create_history_record(
        [params["item"]], params["action"], get_user(), params["section"]
    )
    return jsonify({"success": True}), 201


def init_app(app):
    newsroom.register_resource("history", HistoryResource, HistoryService, _app=app)
