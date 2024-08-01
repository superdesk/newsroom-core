from enum import Enum

PRODUCT_TYPES = ["wire", "agenda", "news_api"]


class ProductType(str, Enum):
    WIRE = "wire"
    AGENDA = "agenda"
    NEWS_API = "news_api"
