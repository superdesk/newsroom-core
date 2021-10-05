
import os
import json
import requests

from urllib.parse import urljoin
from flask import current_app, request, url_for, send_from_directory
from flask_webpack import Webpack


def is_localhost():
    return request and 'localhost' in request.url


def send_asset(filename):
    return send_from_directory(
        os.path.dirname(current_app.config['WEBPACK_MANIFEST_PATH']),
        filename,
    )


session = requests.Session()


class NewsroomWebpack(Webpack):

    def init_app(self, app):
        app.config.setdefault(
            "WEBPACK_MANIFEST_PATH",
            os.path.join(
                app.config["ABS_PATH"].parent,
                "client",
                "dist",
                "manifest.json",
            ) if app.config.get("ABS_PATH") else None,
        )

        super(NewsroomWebpack, self).init_app(app)

        if not app.config.get('DEBUG'):  # let us change debug flag later
            app.before_request(self._refresh_webpack_stats_if_debug)

        app.add_url_rule('/static/dist/<path:filename>', 'asset', send_asset)

    def _refresh_webpack_stats_if_debug(self):
        if current_app.debug or is_localhost():
            self._refresh_webpack_stats()

    def _set_asset_paths(self, app):
        webpack_stats = app.config['WEBPACK_MANIFEST_PATH']
        self.assets_url = app.config['WEBPACK_ASSETS_URL']

        if app.testing:
            self.assets = {}
            return

        if app.config.get('WEBPACK_SERVER_URL'):
            try:
                self.assets = session.get(urljoin(app.config['WEBPACK_SERVER_URL'], 'manifest.json'), timeout=5).json()
                self.assets_url = app.config['WEBPACK_SERVER_URL']
                return
            except requests.exceptions.ConnectionError:
                raise RuntimeError(
                    "Webpack server is not running on {url}".format(url=app.config['WEBPACK_SERVER_URL']))

        try:
            with app.open_resource(webpack_stats, 'r') as stats_json:
                self.assets = json.load(stats_json)
        except IOError:
            if request:
                raise RuntimeError(
                    "Flask-Webpack requires 'WEBPACK_MANIFEST_PATH' to be set and "
                    "it must point to a valid json file.")

    def asset_url_for(self, asset):
        """Override method used by template helpers.

        Make it use internal endpoint if `assets_url` is not set.
        """
        if '//' in asset:
            return asset

        if asset not in self.assets:
            return None

        if self.assets_url:
            return urljoin(self.assets_url, self.assets[asset])

        return url_for('asset', filename=self.assets[asset])
