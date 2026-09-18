import click

from superdesk.core import get_current_async_app

from .cli import newsroom_cli


def elastic_reindex_handler(resource: str, requests_per_second: int = 1000):
    """
    Handler function for elastic reindex operation.

    Args:
        resource: The resource to reindex (must be one of: items, agenda, history)
        requests_per_second: Number of requests per second for reindexing

    Returns:
        The result of the elastic reindex operation

    Raises:
        ValueError: If resource is not one of the allowed values
    """
    valid_resources = ("items", "agenda", "history")
    if resource not in valid_resources:
        raise ValueError(f"Invalid resource '{resource}'. Must be one of: {', '.join(valid_resources)}")

    return get_current_async_app().elastic.reindex(resource, requests_per_second=requests_per_second)


@newsroom_cli.command("elastic_reindex")
@click.option("-r", "--resource", required=True, help="Resource to reindex")
@click.option("-s", "--requests-per-second", default=1000, type=int, help="Number of requests per second")
def elastic_reindex(resource, requests_per_second=1000):
    """
    Reindex a specific resource in Elasticsearch.

    This command rebuilds the Elasticsearch index for the specified resource
    with the ability to control the reindexing speed.
    """
    return elastic_reindex_handler(resource, requests_per_second)
