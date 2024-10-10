from typing import Generic, Any, ClassVar, TypeVar

from superdesk.core.resources.service import AsyncResourceService

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
