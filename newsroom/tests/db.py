from pymongo import MongoClient

from superdesk.core.mongo import get_mongo_client_config
from newsroom import MONGO_PREFIX


async def reset_elastic(app):
    indices = "%s*" % app.config["CONTENTAPI_ELASTICSEARCH_INDEX"]
    es = app.data.elastic.es
    es.indices.delete(indices, ignore=[404])
    await app.data.init_elastic(app)


def drop_mongo(config):
    client_config, dbname = get_mongo_client_config(config)
    client = MongoClient(**client_config)
    client.drop_database(dbname)

    client_config, dbname = get_mongo_client_config(config, prefix=MONGO_PREFIX)
    client = MongoClient(**client_config)
    client.drop_database(dbname)
