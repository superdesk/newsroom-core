from typing import Any, ClassVar, cast
from urllib.parse import urlencode
from pydantic import field_validator, model_validator

from content_api.errors import UnexpectedParameterError
from newsroom.news_api.news.filters_utils import parse_iso_date
from superdesk.core.types import Response
from superdesk.core.types.web import Request
from superdesk.core.resources.fields import Field

from newsroom.search.types import NewshubSearchRequest, SearchFilterFunction
from newsroom.news_api.news.types import NewsApiSearchRequestArgs
from newsroom.news_api.news.search_service import NewsApiSearchServiceAsync, default_search_filters


allowed_exclude_fields = {
    "version",
    "firstcreated",
    "headline",
    "byline",
    "slugline",
}


class NewsAPIFeedSearchArgs(NewsApiSearchRequestArgs):
    allowed_exclude_fields: ClassVar[set[str]] = allowed_exclude_fields

    exclude_ids: list[str] = Field(default_factory=list)

    @field_validator("exclude_ids", mode="before")
    def validate_exclude_ids(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            return value.split(",")

        return value

    @model_validator(mode="before")
    @classmethod
    def validate_not_allowed_feed_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Some fields from the parent class are not allowed in feed's case
        """

        restricted_fields = ["page", "page_size", "sort"]
        for field in restricted_fields:
            if field in values:
                raise UnexpectedParameterError(desc=f"Unexpected parameter ({field})")

        return values


def apply_exclude_ids(request: NewshubSearchRequest[NewsAPIFeedSearchArgs]):
    if request.args.exclude_ids:
        request.search.query.must_not.append({"terms": {"_id": request.args.exclude_ids}})


default_news_feed_filters = [apply_exclude_ids] + default_search_filters


class NewsAPIFeedSearchService(NewsApiSearchServiceAsync):
    search_args_class = NewsAPIFeedSearchArgs
    filters = cast(list[SearchFilterFunction], default_news_feed_filters)

    def build_hateoas(self, req: Request, resp: Response, search_req: NewshubSearchRequest[NewsApiSearchRequestArgs]):
        super().build_hateoas(req, resp, search_req)

        resp.body["_links"].pop("last", None)
        resp.body["_links"].pop("next", None)
        resp.body["_meta"].pop("page", None)

        self._hateoas_set_next_page_links(resp, search_req)

    def _hateoas_set_next_page_links(self, resp: Response, search_req: NewshubSearchRequest[NewsApiSearchRequestArgs]):
        doc = resp.body
        query_params = search_req.args.to_dict(flatten_lists=True)

        if doc["_meta"]["total"] > 0:
            items = list(doc.get("_items") or [])
            last_datetime = items[0].get("versioncreated")
            exclude_ids = []
            for item in items:
                if item.get("versioncreated") != last_datetime:
                    break

                exclude_ids.append(item.get("_id"))

            parsed_datetime = parse_iso_date(last_datetime)
            assert parsed_datetime is not None
            query_params["start_date"] = parsed_datetime.strftime("%Y-%m-%dT%H:%M:%S")
            query_params["exclude_ids"] = ",".join(exclude_ids)

            args = f"?{urlencode(query_params)}" if query_params else ""
            doc["_links"]["next_page"] = {"title": "News Feed", "href": f"news/feed{args}"}
        else:
            args = f"?{urlencode(query_params)}" if query_params else ""
            doc["_links"]["next_page"] = doc["_links"]["self"] = {"title": "News Feed", "href": f"news/feed{args}"}
