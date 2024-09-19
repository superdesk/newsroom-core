from typing import Generic, Any, ClassVar, TypeVar, List, Dict

from superdesk.core.resources.service import AsyncResourceService
from newsroom.utils import get_user_id
from newsroom.core import get_current_wsgi_app

from .model import NewshubResourceModel


NewshubResourceModelType = TypeVar("NewshubResourceModelType", bound=NewshubResourceModel)


class NewshubAsyncResourceService(AsyncResourceService[Generic[NewshubResourceModelType]]):
    clear_item_cache_on_update: ClassVar[bool] = False

    async def on_create(self, docs: list[NewshubResourceModelType]) -> None:
        await super().on_create(docs)
        for doc in docs:
            doc.original_creator = get_user_id()
            doc.version_creator = get_user_id()

    async def on_update(self, updates: dict[str, Any], original: NewshubResourceModelType) -> None:
        await super().on_update(updates, original)
        updates["version_creator"] = get_user_id()

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

    async def update_many(self, lookup: Dict[str, Any], updates: Dict[str, Any]) -> List[str]:
        """Updates multiple resources using a lookup and updates.

        :param lookup: Dictionary for the lookup to find items to update
        :param updates: Dictionary of updates to be applied to each found resource
        :return: List of IDs for the updated resources
        """
        docs_to_update = self.mongo.find(lookup).sort("_id", 1)
        ids: List[str] = []

        async for data in docs_to_update:
            original = self.get_model_instance_from_dict(data)
            await self.on_update(updates, original)
            validated_updates = await self.validate_update(updates, original, etag=None)
            updates_dict = {key: val for key, val in validated_updates.items() if key in updates}
            updates["_etag"] = updates_dict["_etag"] = self.generate_etag(
                validated_updates, self.config.etag_ignore_fields
            )

            # Perform the update in MongoDB
            await self.mongo.update_one({"_id": original.id}, {"$set": updates_dict})

            # Attempt to update Elasticsearch
            try:
                await self.elastic.update(original.id, updates_dict)
            except KeyError:
                pass

            # Handle versioning if applicable
            if self.config.versioning:
                await self.mongo_versioned.insert_one(self._get_versioned_document(validated_updates))

            await self.on_updated(updates, original)
            ids.append(str(original.id))

        return ids
