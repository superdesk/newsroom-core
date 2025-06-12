from typing import Generic, Any, ClassVar, TypeVar

from bson import ObjectId

from superdesk.core.types import SearchRequest, SortParam, ProjectedFieldArg
from superdesk.core.resources.service import (
    AsyncResourceService,
    ElasticsearchResourceCursorAsync,
    MongoResourceCursorAsync,
)

from newsroom.core import get_current_wsgi_app

from .model import NewshubResourceModel


NewshubResourceModelType = TypeVar("NewshubResourceModelType", bound=NewshubResourceModel)


class NewshubAsyncResourceService(AsyncResourceService[Generic[NewshubResourceModelType]]):
    clear_item_cache_on_update: ClassVar[bool] = False

    async def on_create(self, docs: list[NewshubResourceModelType]) -> None:
        from newsroom.auth.utils import get_user_or_none_from_request

        await super().on_create(docs)
        current_user = get_user_or_none_from_request(None)
        if current_user:
            for doc in docs:
                doc.original_creator = current_user.id
                doc.version_creator = current_user.id

    async def on_update(self, updates: dict[str, Any], original: NewshubResourceModelType) -> None:
        from newsroom.auth.utils import get_user_or_none_from_request

        await super().on_update(updates, original)
        current_user = get_user_or_none_from_request(None)
        if current_user:
            updates["version_creator"] = current_user.id

    async def on_updated(self, updates: dict[str, Any], original: NewshubResourceModelType) -> None:
        await super().on_updated(updates, original)
        if self.clear_item_cache_on_update:
            app = get_current_wsgi_app()
            app.cache.delete(str(original.id))

    async def on_deleted(self, doc: NewshubResourceModelType):
        await super().on_deleted(doc)
        if self.clear_item_cache_on_update:
            app = get_current_wsgi_app()
            app.cache.delete(str(doc.id))

    async def find_items_by_ids(self, ids: list[str] | list[ObjectId]) -> list[NewshubResourceModelType]:
        """
        Fetches and returns the entries from database for the given list of IDs
        """
        cursor = await self.search({"_id": {"$in": ids}})
        return await cursor.to_list()

    async def get_all_raw_as_list(self) -> list[dict[str, Any]]:
        """
        Returns the list of all the entries raw as list
        """
        return [entry async for entry in self.get_all_raw()]

    async def find(
        self,
        req: SearchRequest | dict,
        page: int = 1,
        max_results: int = 500,
        sort: SortParam | None = None,
        projection: ProjectedFieldArg | None = None,
        use_mongo: bool = False,
    ) -> ElasticsearchResourceCursorAsync[NewshubResourceModelType] | MongoResourceCursorAsync[
        NewshubResourceModelType
    ]:
        """Find items from the resource

        Note: Overriding super method to set default ``max_results`` to 500

        :param req: SearchRequest instance, or a lookup dictionary, for the search params to be used
        :param page: The page number to retrieve (defaults to 1)
        :param max_results: The maximum number of results to retrieve per page (defaults to 500)
        :param sort: The sort order to use (defaults to resource default sort, or not sorting applied)
        :param projection: The field projections to be applied
        :param use_mongo: If ``True`` will force use mongo, else will attempt elastic first
        :return: An async iterable with ``ResourceModel`` instances
        :raises SuperdeskApiError.notFoundError: If Elasticsearch is not configured
        """

        return await super().find(req, page, max_results, sort, projection, use_mongo)
