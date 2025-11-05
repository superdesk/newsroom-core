from typing import Any

from superdesk.core.types import Request, Response, BaseModel, RestGetResponse
from superdesk.core.module import Module
from superdesk.core.web import EndpointGroup
from superdesk.core.resources.fields import ObjectId

from newsroom.types import ProductResourceModel, SectionEnum
from newsroom.products.utils import get_products_by_company_async

from .utils import post_api_audit, get_company_from_newsapi_request


product_endpoints = EndpointGroup("Account Products", __name__)


def get_product_links(product: ProductResourceModel) -> dict[str, Any]:
    return {
        "search": {
            "href": f"news/search/?products={product.id}",
            "title": "News Search",
        },
        "feed": {
            "href": f"news/feed/?products={product.id}",
            "title": "News Feed",
        },
    }


@product_endpoints.endpoint("account/products", title="Account Products Search", methods=["GET"])
async def get_products(request: Request) -> Response:
    company = get_company_from_newsapi_request(request)
    products = await get_products_by_company_async(company, None, SectionEnum.NEWS_API)
    await post_api_audit(request, [str(product.id) for product in products])

    response = RestGetResponse(
        _items=[
            {
                "_id": product.id,
                "name": product.name,
                "description": product.description,
                "_links": get_product_links(product),
            }
            for product in products
        ],
        _meta={
            "page": 1,
            "max_results": 200,
            "total": len(products),
        },
    )

    return Response(response)


class GetProductArgs(BaseModel):
    product_id: ObjectId


@product_endpoints.endpoint("account/products/<string:product_id>", title="Get Account Product")
async def get_product(args: GetProductArgs, params: None, request: Request) -> Response:
    company = get_company_from_newsapi_request(request)
    company_product_ids = [product._id for product in company.products if product.section == SectionEnum.NEWS_API]
    if args.product_id not in company_product_ids:
        return await request.abort(404, "Product not found 1.")

    product = await ProductResourceModel.get_service().find_by_id(args.product_id)
    if not product:
        return await request.abort(404, "Product not found 2.")

    await post_api_audit(request, [str(product.id)])
    return Response(
        {
            "_id": product.id,
            "name": product.name,
            "description": product.description,
            "_links": get_product_links(product),
        }
    )


module = Module(
    "newsroom.news_api.products",
    endpoints=[product_endpoints],
)
