from flask import current_app as app
from newsroom import MONGO_PREFIX


def reset_elastic():
    app.data.elastic.drop_index()


def drop_mongo():
    dbname = app.config["MONGO_DBNAME"]
    dbconn = app.data.mongo.pymongo(prefix=MONGO_PREFIX).cx
    dbconn.drop_database(dbname)
    dbconn.close()
