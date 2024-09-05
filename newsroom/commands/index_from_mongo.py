import click
from quart.cli import with_appcontext

from superdesk.core import get_current_app
from superdesk.commands.index_from_mongo import IndexFromMongo
from newsroom.mongo_utils import (
    index_elastic_from_mongo,
    index_elastic_from_mongo_from_timestamp,
)

from .cli import newsroom_cli


@newsroom_cli.command("index_from_mongo_period")
@click.option("-h", "--hours", default=None, help="Number of hours to index")
@click.option("-c", "--collection", default=None, help="Name of the collection to index")
@click.option("-t", "--timestamp", default=None, help="Timestamp to start indexing from")
@click.option("-d", "--direction", type=click.Choice(["older", "newer"]), default="older", help="Direction of indexing")
@with_appcontext
def index_from_mongo_period(hours, collection, timestamp, direction):
    """
    It allows to reindex up to a certain period.
    """
    app = get_current_app()
    print("Checking if elastic index exists, a new one will be created if not")
    app.data.init_elastic(app)
    print("Elastic index check has been completed")

    if timestamp:
        index_elastic_from_mongo_from_timestamp(collection, timestamp, direction)
    else:
        index_elastic_from_mongo(hours=hours, collection=collection)


@newsroom_cli.command("index_from_mongo")
@click.option("--from", "-f", "collection_name", help="Name of the collection to index")
@click.option("--all", "all_collections", is_flag=True, help="Index all collections")
@click.option("--page-size", "-p", default=500, help="Page size for indexing")
@with_appcontext
def index_from_mongo(collection_name, all_collections, page_size):
    """Index the specified mongo collection in the specified elastic collection/type.

    This will use the default APP mongo DB to read the data and the default Elastic APP index.

    Use ``-f all`` to index all collections.

    Example:
    ::

        $ flask newsroom index_from_mongo --from=items
        $ flask newsroom index_from_mongo --all

    """
    IndexFromMongo().run(collection_name, all_collections, page_size, None, None)
