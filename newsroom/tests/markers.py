from pytest import mark


# Forces ``newsroom.auth.oauth.blueprint`` to be registered regardless of the Google config
# Sets ``app.config["FORCE_ENABLE_GOOGLE_OAUTH"]`` to True
enable_google_login = mark.enable_google_login

# Adds ``newsroom.auth.saml`` to ``app.config["INSTALLED_APPS"]``
# This registers SAML views to the auth blueprint
enable_saml = mark.enable_saml

# Mark tests that require celery
requires_async_celery = mark.requires_async_celery

skip_auto_wire_items = mark.skip_auto_wire_items
skip_auto_agenda_items = mark.skip_auto_agenda_items
