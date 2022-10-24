import superdesk
import newsroom


class UIConfigResource(newsroom.Resource):
    """UI Config for Preview and Details view based on section name

    For example:
    {
        "_id": "wire",
        "preview": {
            "slugline": {"displayed": true},
            "genre": {"displayed": false},
        },
        "details": {
            "slugline": {"displayed": false},
            "genre": {"displayed": true},
        }
    }
    """

    schema = {
        "_id": {"type": "string", "required": True, "unique": True},
        "preview": {"type": "dict"},
        "details": {"type": "dict"},
        "list": {"type": "dict"},
        "advanced_search_tabs": {"type": "dict"},
        "multi_select_topics": {"type": "boolean", "default": False},
        "search": {
            "type": "boolean",
        },
        "enable_global_topics": {"type": "boolean", "default": True},
        "open_coverage_content_in_same_page": {"type": "boolean", "default": False},
        "init_version": {"type": "integer"},
    }
    datasource = {"source": "ui_config"}
    item_methods = ["GET"]
    resource_methods = ["GET"]


class UIConfigService(newsroom.Service):
    def get_section_config(self, section_name):
        """Get the section config"""
        config = self.find_one(req=None, _id=section_name)
        if not config:
            return {}
        return config


def init_app(app):
    superdesk.register_resource("ui_config", UIConfigResource, UIConfigService, _app=app)
