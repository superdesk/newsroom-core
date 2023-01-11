from newsroom.auth import get_company
from newsroom.news_api.utils import (
    remove_internal_renditions,
    check_association_permission,
)
from newsroom.products.products import get_products_by_company
from .ninjs import NINJSFormatter


class NINJSFormatter2(NINJSFormatter):
    """
    Overload the NINJSFormatter and add the associations as a field to copy
    """

    def __init__(self):
        self.direct_copy_properties += ("associations",)

    def _transform_to_ninjs(self, item):
        company = get_company()
        products = get_products_by_company(company)
        if not check_association_permission(item, products):
            item.pop("associations", None)
        return remove_internal_renditions(super()._transform_to_ninjs(item))
