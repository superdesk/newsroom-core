from superdesk.commands.index_from_mongo import IndexFromMongo

from newsroom.mongo_utils import index_elastic_from_mongo, index_elastic_from_mongo_from_timestamp

from .manager import app, manager


@manager.option('-h', '--hours', dest='hours', default=None)
@manager.option('-c', '--collection', dest='collection', default=None)
@manager.option('-t', '--timestamp', dest='timestamp', default=None)
@manager.option('-d', '--direction', dest='direction', choices=['older', 'newer'], default='older')
def index_from_mongo_period(hours, collection, timestamp, direction):
    """
    It allows to reindex up to a certain period.
    """
    print('Checking if elastic index exists, a new one will be created if not')
    app.data.init_elastic(app)
    print('Elastic index check has been completed')

    if timestamp:
        index_elastic_from_mongo_from_timestamp(collection, timestamp, direction)
    else:
        index_elastic_from_mongo(hours=hours, collection=collection)


@manager.option('--from', '-f', dest='collection_name')
@manager.option('--all', action='store_true', dest='all_collections')
@manager.option('--page-size', '-p', default=500)
def index_from_mongo(collection_name, all_collections, page_size):
    """Index the specified mongo collection in the specified elastic collection/type.

    This will use the default APP mongo DB to read the data and the default Elastic APP index.

    Use ``-f all`` to index all collections.

    Example:
    ::

        $ python manage.py index_from_mongo --from=items
        $ python manage.py index_from_mongo --all

    """
    IndexFromMongo().run(collection_name, all_collections, page_size, None)
