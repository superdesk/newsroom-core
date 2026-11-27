from bson import ObjectId

from newsroom.limiter import limiter


def get_test_config(
    config: dict | None = None, config_path: str = "newsroom.web.default_settings", test_name: str = "test"
) -> dict:
    db_name = f"newsroom_{test_name}"
    mongo_uri = f"mongodb://localhost/{db_name}"

    return {
        "_default_config": config_path,
        "CONTENTAPI_URL": "http://localhost:5400",
        "ELASTICSEARCH_INDEX": db_name,
        "CONTENTAPI_ELASTICSEARCH_INDEX": db_name,
        "MONGO_DBNAME": db_name,
        "CONTENTAPI_MONGO_DBNAME": db_name,
        "MONGO_URI": mongo_uri,
        "CONTENTAPI_MONGO_URI": mongo_uri,
        "SERVER_NAME": "localhost:5050",
        "WTF_CSRF_ENABLED": False,
        "DEBUG": True,
        "TESTING": True,
        "WEBPACK_ASSETS_URL": None,
        "BABEL_DEFAULT_TIMEZONE": "Europe/Prague",
        "DEFAULT_TIMEZONE": "Europe/Prague",
        "NEWS_API_ENABLED": True,
        "AUTH_SERVER_SHARED_SECRET": "2kZOf0VI9T70vU9uMlKLyc5GlabxVgl6",
        "SECRET_KEY": "foo",
        "CELERY_TASK_ALWAYS_EAGER": True,
        "MAIL_USE_CELERY": False,

        "ELASTICSEARCH_FORCE_REFRESH": True,
        "CACHE_TYPE": "null",
        "MONGO_CONNECT": False,
        "MONGO_MAX_POOL_SIZE": 1,

        **(config or {}),
    }


def set_limiter_key_function():
    limiter_key = str(ObjectId())

    async def limiter_key_function():
        return limiter_key

    limiter.key_function = limiter_key_function
