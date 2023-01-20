import os
import flask
import jinja2

from newsroom.factory import BaseNewsroomApp
from newsroom.template_filters import (
    datetime_short,
    datetime_long,
    time_short,
    date_short,
    plain_text,
    word_count,
    char_count,
    newsroom_config,
    is_admin,
    hash_string,
    date_header,
    get_date,
    get_multi_line_message,
    sidenavs_by_names,
    sidenavs_by_group,
    get_company_sidenavs,
    is_admin_or_account_manager,
    authorized_settings_apps,
    theme_url,
    to_json,
)
from newsroom.notifications.notifications import get_initial_notifications
from newsroom.limiter import limiter
from newsroom.celery_app import init_celery
from newsroom.settings import SettingsApp
from newsroom.webpack import NewsroomWebpack


class NewsroomWebApp(BaseNewsroomApp):
    """Newsroom web app.

    Usage::

        from newsroom.web import NewsroomWebApp

        app = NewsroomWebApp(__name__)
        app.run()
    """

    INSTANCE_CONFIG = "settings.py"

    def __init__(self, import_name=__package__, config=None, **kwargs):
        self.download_formatters = {}
        self.sections = []
        self.sidenavs = []
        self.settings_apps = []
        self.dashboards = []
        self._theme_folders = []

        # avoid event sockets on these
        self.generate_renditions = None
        self.generate_embed_renditions = None

        super(NewsroomWebApp, self).__init__(import_name=import_name, config=config, **kwargs)

        self.theme_folder = os.path.join(self.config["SERVER_PATH"], "theme")
        self._theme_folders = [
            folder
            for folder in [
                self.theme_folder,
                os.path.join(self.config["SERVER_PATH"], "templates"),
                self.template_folder,
                self.static_folder,
            ]
            if os.path.exists(folder)
        ]

        self._setup_jinja()
        self._setup_limiter()
        self._setup_celery()
        self._setup_theme()
        self._setup_assets()

    def load_app_default_config(self):
        """
        Loads default app configuration
        """
        # default config from `content_api.app.settings`
        super().load_app_default_config()
        # default config from `newsroom.web.default_settings`
        self.config.from_object("newsroom.web.default_settings")

    def load_app_instance_config(self):
        """
        Loads instance configuration defined on the newsroom-app repo level
        """
        # config from newsroom-app settings.py file
        super().load_app_instance_config()
        # config from env var
        self.config.from_envvar("NEWSROOM_SETTINGS", silent=True)

    def _setup_jinja(self):
        self.add_template_filter(to_json, name="tojson")
        self.add_template_filter(datetime_short)
        self.add_template_filter(datetime_long)
        self.add_template_filter(date_header)
        self.add_template_filter(plain_text)
        self.add_template_filter(time_short)
        self.add_template_filter(date_short)
        self.add_template_filter(word_count)
        self.add_template_filter(char_count)
        self.add_template_global(get_company_sidenavs, "sidenavs")
        self.add_template_global(sidenavs_by_names)
        self.add_template_global(sidenavs_by_group)
        self.add_template_global(is_admin_or_account_manager)
        self.add_template_global(authorized_settings_apps)
        self.add_template_global(newsroom_config)
        self.add_template_global(is_admin)
        self.add_template_global(get_initial_notifications)
        self.add_template_global(hash_string, "hash")
        self.add_template_global(get_date, "get_date")
        self.add_template_global(self.settings_apps, "settings_apps")
        self.add_template_global(get_multi_line_message)
        self.add_template_global(theme_url)

        jinja2_loaders = [jinja2.FileSystemLoader(folder) for folder in self._theme_folders]

        self.jinja_loader = jinja2.ChoiceLoader(jinja2_loaders)

    def _setup_limiter(self):
        limiter.init_app(self)

    def _setup_celery(self):
        init_celery(self)

    def _setup_assets(self):
        NewsroomWebpack(self)

    def _setup_theme(self):
        self.add_url_rule(
            self.static_url_path.replace("static", "theme") + "/<path:filename>",
            endpoint="theme",
            host=self.static_host,
            view_func=self.send_theme_file,
        )

    def download_formatter(self, _format, formatter, name, types, assets=None):
        """Register new download formatter.

        :param _format: format id
        :param formatter: formatter class, extending :class:`newsroom.formatter.BaseFormatter` class.
        :param name: human readable name
        :param types: list of supported types, eg. ``['wire', 'agenda']``
        :param types: list of supported assets, eg. ``['picture']``
        """
        self.download_formatters[_format] = {
            "format": _format,
            "formatter": formatter,
            "name": name,
            "types": types,
            "assets": assets,
        }

    def send_theme_file(self, filename):
        if os.path.exists(os.path.join(self.theme_folder, filename)):
            return flask.send_from_directory(self.theme_folder, filename)
        return self.send_static_file(filename)

    def section(self, _id, name, group, search_type=None):
        """Define new app section.

        App sections are used for permissions in company settings,
        and for grouping products.

        You can define new sections in module :meth:`init_app` method::

            def init_app(app):
                app.section('foo', 'Foo', 'wire)

        And then you can use it in views as decorator and it will check if user
        has section active::

            from newsroom.decorators import section

            @blueprint.route('/foo')
            @section('foo')
            def example():
                # user company has section foo enabled
                return flask.render_template('example_index.html)

        You can also specify ``section`` param in sidenav and it will filter out
        menu items with sections which are not enabled for company.

        :param _id: section _id
        :param name: section name
        """
        self.sections.append({"_id": _id, "name": name, "group": group, "search_type": search_type})

    def sidenav(
        self,
        name,
        endpoint=None,
        icon=None,
        group=0,
        section=None,
        blueprint=None,
        badge=None,
        url=None,
        secondary_endpoints=[],
        locale=None,
    ):
        """Register an item in sidebar menu.

        Use in module :meth:`init_app` method::

            def init_app(app):
                app.section('foo', 'Foo', 'wire')

        :param name: user readable name
        :param endpoint: endpoint name, used with :meth:`flask.url_for`
        :param icon: css icon class name
        :param group: group number, ``0`` by default, up to ``9``.
        :param section: section ``_id``, will be only visible if user has section enabled.
        :param blueprint: blueprint name, will be only visible if blueprint is active
        :param badge: badge id - will add badge html markup with given id
        :param url: external url - will add external link badge and use target=_blank for link
        :param secondary_endpoints: registers other endpoints (internal navigations) of a sidenav's page
        :param locale: set locale if link is language specific, null will be displayed for all locales
        """
        if endpoint is None and url is None:
            raise ValueError("please specify endpoint or url")

        self.sidenavs.append(
            {
                "name": name,
                "endpoint": endpoint,
                "icon": icon,
                "group": group,
                "section": section,
                "blueprint": blueprint,
                "badge": badge,
                "url": url,
                "secondary_endpoints": secondary_endpoints,
                "locale": locale,
            }
        )

    def settings_app(self, app, name, weight=1000, data=None, allow_account_mgr=False):
        self.settings_apps.append(
            SettingsApp(
                _id=app,
                name=name,
                data=data,
                weight=weight,
                allow_account_mgr=allow_account_mgr,
            )
        )

    def dashboard(self, _id, name, cards=[]):
        """Define new dashboard

        :param _id: id of the dashboard
        :param name: display name of the dashboard
        :param cards: list of cards id related to the dashboard to
        populate the drop down in dashboard config.
        """
        self.dashboards.append({"_id": _id, "name": name, "cards": cards})


def get_app(config=None, **kwargs):
    return NewsroomWebApp(__name__, config=config, **kwargs)
