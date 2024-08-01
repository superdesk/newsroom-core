from superdesk.core import get_current_app, get_app_config
from newsroom import MONGO_PREFIX


def reset_elastic():
    get_current_app().data.elastic.drop_index()


def drop_mongo():
    dbname = get_app_config("MONGO_DBNAME")
    dbconn = get_current_app().data.mongo.pymongo(prefix=MONGO_PREFIX).cx
    dbconn.drop_database(dbname)
