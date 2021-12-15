from superdesk.commands.flush_elastic_index import FlushElasticIndex

from .manager import manager


@manager.command
def elastic_rebuild():
    """
    It removes elastic index, creates a new one(s) and index it from mongo.

    Example:
    ::

        $ python manage.py elastic_rebuild

    """
    FlushElasticIndex().run(sd_index=True, capi_index=True)
