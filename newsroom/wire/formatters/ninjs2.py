from newsroom.auth.utils import get_company_or_none_from_request
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
        company = get_company_or_none_from_request(None)
        # TODO-ASYNC: replace then formatters are async
        products = get_products_by_company(company.to_dict() if company else None)
        if not check_association_permission(item, products):
            item.pop("associations", None)
        return remove_internal_renditions(super()._transform_to_ninjs(item))
