from superdesk import get_resource_service

from newsroom.types import NavigationModel
from newsroom.core.resources.service import NewshubAsyncResourceService


class NavigationsService(NewshubAsyncResourceService[NavigationModel]):
    resource_name = "navigations"

    async def on_delete(self, doc: NavigationModel):
        """Remove references in products to this navigation entry once it is deleted"""
        from newsroom.products import ProductsService

        await super().on_delete(doc)

        navigation = doc.id
        products_cursor = await ProductsService().search({"navigations": str(navigation)})

        for product in await products_cursor.to_list_raw():
            product["navigations"].remove(navigation)
            await ProductsService().update(product["_id"], product)
