from superdesk.commands.flush_elastic_index import FlushElasticIndex
from .cli import newsroom_cli


@newsroom_cli.command("elastic_rebuild")
async def elastic_rebuild():
    """
    It removes elastic index, creates a new one(s) and index it from mongo.

    Example:
    ::

        $ python manage.py elastic_rebuild

    """
    await FlushElasticIndex().run(sd_index=True, capi_index=True)
