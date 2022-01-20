from . import oauth2


def init_app(app):
    oauth2.config_oauth(app)
