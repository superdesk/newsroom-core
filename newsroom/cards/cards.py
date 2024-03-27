import typing
import newsroom

from newsroom.types import DashboardCardType


class CardsResource(newsroom.Resource):
    """
    Cards schema
    """

    schema = {
        "label": {"type": "string", "unique": True, "required": True},
        "type": {
            "type": "string",
            "required": True,
            "nullable": False,
            "allowed": list(typing.get_args(DashboardCardType)),
        },
        "config": {
            "type": "dict",
        },
        "order": {"type": "integer", "nullable": True},
        # to indicate that the card belongs to which dashboard it belongs
        "dashboard": {
            "type": "string",
            "required": True,
        },
        "original_creator": newsroom.Resource.rel("users"),
        "version_creator": newsroom.Resource.rel("users"),
    }
    datasource = {"source": "cards", "default_sort": [("order", 1), ("label", 1)]}
    item_methods = ["GET", "PATCH", "DELETE"]
    resource_methods = ["GET", "POST"]


class CardsService(newsroom.Service):
    pass
