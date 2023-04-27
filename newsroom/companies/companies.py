from eve.utils import config
from content_api import MONGO_PREFIX

from superdesk import get_resource_service
import newsroom
from newsroom.companies.utils import get_company_section_names, get_company_product_ids


class CompaniesResource(newsroom.Resource):
    """
    Company schema
    """

    schema = {
        "name": {"type": "string", "unique": True, "required": True},
        "url": {"type": "string"},
        "sd_subscriber_id": {"type": "string"},
        "is_enabled": {"type": "boolean", "default": True},
        "contact_name": {"type": "string"},
        "contact_email": {"type": "string"},
        "phone": {"type": "string"},
        "country": {"type": "string"},
        "expiry_date": {
            "type": "datetime",
            "nullable": True,
            "required": False,
        },
        "sections": {
            "type": "dict",
            "nullable": True,
        },
        "archive_access": {
            "type": "boolean",
        },
        "events_only": {
            "type": "boolean",
            "default": False,
        },
        "restrict_coverage_info": {
            "type": "boolean",
            "default": False,
        },
        "company_type": {
            "type": "string",
            "nullable": True,
        },
        "account_manager": {"type": "string"},
        "monitoring_administrator": {"type": "objectid"},
        "allowed_ip_list": {"type": "list", "mapping": {"type": "string"}},
        "original_creator": newsroom.Resource.rel("users"),
        "version_creator": newsroom.Resource.rel("users"),
        "products": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "_id": newsroom.Resource.rel("products"),
                    "seats": {"type": "number", "default": 0},
                    "section": {"type": "string", "default": "wire"},
                },
            },
        },
    }

    datasource = {"source": "companies", "default_sort": [("name", 1)]}
    item_methods = ["GET", "PATCH", "DELETE"]
    resource_methods = ["GET", "POST"]
    mongo_prefix = MONGO_PREFIX
    internal_resource = True
    mongo_indexes = {
        "name_1": (
            [("name", 1)],
            {"unique": True, "collation": {"locale": "en", "strength": 2}},
        ),
    }


class CompaniesService(newsroom.Service):
    def on_update(self, updates, original):
        if "sections" in updates:
            original_products = updates.get("products") or original.get("products") or []
            enabled_sections = [section for section, active in updates.get("sections").items() if active]
            new_products = [product for product in original_products if product.get("section") in enabled_sections]

            if len(new_products) != len(original_products):
                updates["products"] = new_products

    def on_updated(self, updates, original):
        original_section_names = get_company_section_names(original)
        original_product_ids = get_company_product_ids(original)

        updated_section_names = get_company_section_names(updates) if "sections" in updates else original_section_names
        updated_product_ids = get_company_product_ids(updates) if "products" in updates else original_product_ids

        if original_section_names != updated_section_names or original_product_ids != updated_product_ids:
            user_service = get_resource_service("users")
            for user in user_service.get(req=None, lookup={"company": original[config.ID_FIELD]}):
                user_updates = {
                    "sections": {
                        section: enabled and section in updated_section_names
                        for section, enabled in (updates.get("sections") or original.get("sections") or {}).items()
                    },
                    "products": [
                        product
                        for product in updates.get("products") or original.get("products") or []
                        if product.get("section") in updated_section_names and product.get("_id") in updated_product_ids
                    ],
                }
                user_service.patch(user[config.ID_FIELD], updates=user_updates)
