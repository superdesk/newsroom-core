import click
from quart.cli import with_appcontext

from superdesk.core import get_current_app
from .cli import newsroom_cli


@newsroom_cli.cli.command("elastic_reindex")
@click.option("-r", "--resource", required=True, help="Resource to reindex")
@click.option("-s", "--requests-per-second", default=1000, type=int, help="Number of requests per second")
@with_appcontext
def elastic_reindex(resource, requests_per_second=1000):
    assert resource in ("items", "agenda", "history")
    return get_current_app().data.elastic.reindex(resource, requests_per_second=requests_per_second)
