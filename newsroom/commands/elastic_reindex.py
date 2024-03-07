from flask import current_app as app

from .manager import manager


@manager.command
@manager.option("-r", "--resource", dest='resource')
def elastic_reindex(resource):
    assert resource in ("items", "agenda", "history")
    return app.data.elastic.reindex(resource)
