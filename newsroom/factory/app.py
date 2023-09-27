"""
Newsroom Flask app
------------------

This module implements WSGI application extending eve.Eve
"""

import os
import re
import pathlib
import importlib

import eve
import flask
import newsroom
import sentry_sdk

from flask_mail import Mail
from flask_caching import Cache
from superdesk.storage import AmazonMediaStorage, SuperdeskGridFSMediaStorage
from superdesk.datalayer import SuperdeskDataLayer
from superdesk.json_utils import SuperdeskJSONEncoder
from superdesk.validator import SuperdeskValidator
from superdesk.logging import configure_logging
from superdesk.errors import SuperdeskApiError
from superdesk.cache import cache_backend
from elasticapm.contrib.flask import ElasticAPM
from sentry_sdk.integrations.flask import FlaskIntegration

from newsroom.auth import SessionAuth
from newsroom.utils import is_json_request
from newsroom.gettext import setup_babel


NEWSROOM_DIR = pathlib.Path(__file__).resolve().parent.parent


class BaseNewsroomApp(eve.Eve):
    """The base Newsroom app class"""

    SERVICE_NAME = "Newsroom"
    DATALAYER = SuperdeskDataLayer
    AUTH_SERVICE = SessionAuth
    INSTANCE_CONFIG = None

    def __init__(self, import_name=__package__, config=None, testing=False, **kwargs):
        """Override __init__ to do Newsroom specific config and still be able
        to create an instance using ``app = Newsroom()``
        """

        self._testing = testing
        self._general_settings = {}
        self.babel_tzinfo = None
        self.babel_locale = None
        self.babel_translations = None
        self.mail = None
        self.cache = None
        self.static_folder = None
        self.apm = None
        self.__self__ = self
        self.__func__ = None
        self._superdesk_cache = None

        if config is None:
            config = {}

        super(BaseNewsroomApp, self).__init__(
            import_name,
            data=self.DATALAYER,
            auth=self.AUTH_SERVICE,
            template_folder=os.path.join(NEWSROOM_DIR, "templates"),
            static_folder=os.path.join(NEWSROOM_DIR, "static"),
            validator=SuperdeskValidator,
            settings=config,
            **kwargs,
        )
        self.json_encoder = SuperdeskJSONEncoder
        self.data.json_encoder_class = SuperdeskJSONEncoder

        newsroom.flask_app = self

        self.setup_error_handlers()
        self.setup_sentry()
        self.setup_apm()
        self.setup_media_storage()
        self.setup_babel()
        self.setup_apps(self.config["CORE_APPS"])
        if not self.config.get("BEHAVE"):
            # workaround for core 2.3 adding planning to installed apps
            self.setup_apps(self.config.get("INSTALLED_APPS", []))
        # load blueprints after apps just in case some views are added by apps
        self.setup_blueprints(self.config["BLUEPRINTS"])
        self.setup_email()
        self.setup_cache()

        if not self.config.get("TESTING"):
            configure_logging(self.config.get("LOG_CONFIG_FILE"))

    def load_app_default_config(self):
        """
        Loads default app configuration
        """
        self.config.from_object("content_api.app.settings")

    def load_app_instance_config(self):
        """
        Loads instance configuration defined on the newsroom-app repo level
        """
        if not self._testing and self.INSTANCE_CONFIG:
            try:
                self.config.from_pyfile(os.path.join(os.getcwd(), self.INSTANCE_CONFIG))
            except FileNotFoundError:
                pass

    def load_config(self):
        # Override Eve.load_config in order to get default_settings
        super(BaseNewsroomApp, self).load_config()

        self.config.setdefault("DOMAIN", {})
        self.config.setdefault("SOURCES", {})
        self.load_app_default_config()
        self.load_app_instance_config()

        # now we have to do this again to override newsrom default and instance config
        self.config.update(self.settings or {})

    def setup_media_storage(self):
        if self.config.get("AMAZON_CONTAINER_NAME"):
            self.media = AmazonMediaStorage(self)
        else:
            self.media = SuperdeskGridFSMediaStorage(self)

    def setup_babel(self):
        self.config.setdefault("BABEL_TRANSLATION_DIRECTORIES", os.path.join(NEWSROOM_DIR, "translations"))

        if self.config.get("TRANSLATIONS_PATH"):
            self.config["BABEL_TRANSLATION_DIRECTORIES"] = ";".join(
                [
                    str(self.config["BABEL_TRANSLATION_DIRECTORIES"]),
                    str(self.config["TRANSLATIONS_PATH"]),
                ]
            )

        # avoid events on this
        self.babel_tzinfo = None
        self.babel_locale = None
        self.babel_translations = None
        setup_babel(self)

    def setup_blueprints(self, modules):
        """Setup configured blueprints."""
        for name in modules:
            mod = importlib.import_module(name)

            if getattr(mod, "blueprint"):
                self.register_blueprint(mod.blueprint)

    def setup_apps(self, apps):
        """Setup configured apps."""
        for name in apps:
            mod = importlib.import_module(name)
            if hasattr(mod, "init_app"):
                mod.init_app(self)

    def setup_email(self):
        self.mail = Mail(self)

    def setup_cache(self):
        cache_backend.init_app(self)
        self.cache = Cache(self)

    def setup_error_handlers(self):
        def assertion_error(err):
            return flask.jsonify({"error": err.args[0] if err.args else 1}), 400

        def render_404(err):
            if flask.request and is_json_request(flask.request):
                return flask.jsonify({"code": 404}), 404
            return flask.render_template("404.html"), 404

        def render_403(err):
            if flask.request and is_json_request(flask.request):
                return (
                    flask.jsonify(
                        {
                            "code": 403,
                            "error": str(err),
                            "info": getattr(err, "description", None),
                        }
                    ),
                    403,
                )
            return flask.render_template("403.html"), 403

        def superdesk_api_error(err):
            error_code = err.status_code or 500
            return flask.jsonify({"error": err.message or "", "message": err.payload, "code": error_code}), error_code

        self.register_error_handler(AssertionError, assertion_error)
        self.register_error_handler(404, render_404)
        self.register_error_handler(403, render_403)
        self.register_error_handler(SuperdeskApiError, superdesk_api_error)

    def general_setting(
        self,
        _id,
        label,
        type="text",
        default=None,
        weight=0,
        description=None,
        min=None,
        client_setting=False,
    ):
        self._general_settings[_id] = {
            "type": type,
            "label": label,
            "weight": weight,
            "default": default,
            "description": description,
            "min": min,
            "client_setting": client_setting,
        }

        if flask.g:  # reset settings cache
            flask.g.settings = None

    def setup_apm(self):
        if self.config.get("APM_SERVER_URL") and self.config.get("APM_SECRET_TOKEN"):
            self.config["ELASTIC_APM"] = {
                "DEBUG": self.debug,
                "ENVIRONMENT": self._get_apm_environment(),
                "SERVICE_NAME": self.config.get("APM_SERVICE_NAME")
                or self.config.get("SITE_NAME")
                or self.SERVICE_NAME,
                "SERVER_URL": self.config["APM_SERVER_URL"],
                "SECRET_TOKEN": self.config["APM_SECRET_TOKEN"],
                "TRANSACTIONS_IGNORE_PATTERNS": ["^OPTIONS"],
            }

            self.apm = ElasticAPM(self)

    def register_resource(self, resource, settings):
        """In superdesk we have a workaround for mongo indexes, so now we need a workaround here."""
        if settings.get("mongo_indexes__init") and not settings.get("mongo_indexes"):
            settings["mongo_indexes"] = settings["mongo_indexes__init"]
        super().register_resource(resource, settings)
        if settings.get("regex_url"):  # fix hateoas
            self.config["DOMAIN"][resource]["url"] = settings["regex_url"]
        elif "<regex(" in settings.get("url"):
            self.logger.warning("Consider adding regex_url config to resource %s to fix HATEOAS", resource)

    def setup_sentry(self):
        if self.config.get("SENTRY_DSN"):
            sentry_sdk.init(
                dsn=self.config["SENTRY_DSN"],
                integrations=[FlaskIntegration()],
            )

    def _get_apm_environment(self):
        if self.config.get("CLIENT_URL"):
            if re.search(r"-(dev|demo|test|staging)", self.config["CLIENT_URL"]):
                return "staging"
            if "localhost" in self.config["CLIENT_URL"] or self.debug:
                return "testing"
        return "production"
