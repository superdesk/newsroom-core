from flask import current_app as app

from .manager import manager


@manager.option("-r", "--resource", dest="resource")
@manager.option("-s", "--requests-per-second", dest="requests_per_second", type=int)
def elastic_reindex(resource, requests_per_second=1000):
    assert resource in ("items", "agenda", "history")
    return app.data.elastic.reindex(resource, requests_per_second=requests_per_second)
