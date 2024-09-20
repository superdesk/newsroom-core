import os
from pathlib import Path
from pytest import fixture
import asyncio
import contextvars
import traceback
import functools

from bson import ObjectId
from quart import Quart, Config

from superdesk.cache import cache

from newsroom.web.factory import get_app
from newsroom.tests import markers
from newsroom.limiter import limiter

from .db import reset_elastic, drop_mongo

root = (Path(__file__).parent / "..").resolve()


class Task311(asyncio.tasks.Task):
    """
    This is backport of Task from CPython 3.11
    It's needed to allow context passing
    """

    def __init__(self, coro, *, loop=None, name=None, context=None):
        super(asyncio.tasks.Task, self).__init__(loop=loop)
        if self._source_traceback:
            del self._source_traceback[-1]
        if not asyncio.coroutines.iscoroutine(coro):
            # raise after Future.__init__(), attrs are required for __del__
            # prevent logging for pending task in __del__
            self._log_destroy_pending = False
            raise TypeError(f"a coroutine was expected, got {coro!r}")

        if name is None:
            self._name = f"Task-{asyncio.tasks._task_name_counter()}"
        else:
            self._name = str(name)

        self._num_cancels_requested = 0
        self._must_cancel = False
        self._fut_waiter = None
        self._coro = coro
        if context is None:
            self._context = contextvars.copy_context()
        else:
            self._context = context

        self._loop.call_soon(self._Task__step, context=self._context)
        asyncio.tasks._register_task(self)


def task_factory(loop, coro, context=None):
    stack = traceback.extract_stack()
    for frame in stack[-2::-1]:
        package_name = Path(frame.filename).parts[-2]
        if package_name != "asyncio":
            if package_name == "pytest_asyncio":
                # This function was called from pytest_asyncio, use shared context
                break
            else:
                # This function was called from somewhere else, create context copy
                context = None
            break
    return Task311(coro, loop=loop, context=context)


@fixture(scope="session")
def event_loop():
    """
    This fixture is used by pytest-asyncio to run test's setup/run/teardown.
    It's needed to share contextvars between these stages.
    This breaks context isolation for tasks, so we need to check calling context there
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    context = contextvars.copy_context()
    loop.set_task_factory(functools.partial(task_factory, context=context))
    asyncio.set_event_loop(loop)
    return loop


def update_config(conf):
    conf["CONTENTAPI_URL"] = "http://localhost:5400"
    conf["ELASTICSEARCH_INDEX"] = conf["CONTENTAPI_ELASTICSEARCH_INDEX"] = "newsroom_test"
    conf["MONGO_DBNAME"] = conf["CONTENTAPI_MONGO_DBNAME"] = "newsroom_test"
    conf["MONGO_URI"] = conf["CONTENTAPI_MONGO_URI"] = "mongodb://localhost/newsroom_test"
    conf["SERVER_NAME"] = "localhost:5050"
    conf["WTF_CSRF_ENABLED"] = False
    conf["DEBUG"] = True
    conf["TESTING"] = True
    conf["WEBPACK_ASSETS_URL"] = None
    conf["BABEL_DEFAULT_TIMEZONE"] = "Europe/Prague"
    conf["DEFAULT_TIMEZONE"] = "Europe/Prague"
    conf["NEWS_API_ENABLED"] = True
    conf["AUTH_SERVER_SHARED_SECRET"] = "secret123"
    conf["SECRET_KEY"] = "foo"
    conf["CELERY_TASK_ALWAYS_EAGER"] = True
    return conf


def get_mongo_uri(key, dbname):
    """Read mongo uri from env variable and replace dbname.

    :param key: env variable name
    :param dbname: mongo db name to use
    """
    env_uri = os.environ.get(key, "mongodb://localhost/test")
    env_host = env_uri.rsplit("/", 1)[0]
    return "/".join([env_host, dbname])


@fixture
async def app(request):
    cfg = Config(root)
    update_config(cfg)

    active_markers = [mark.name for mark in request.node.own_markers]

    if markers.enable_google_login.name in active_markers:
        cfg["FORCE_ENABLE_GOOGLE_OAUTH"] = True

    if markers.enable_saml.name in active_markers:
        cfg.setdefault("INSTALLED_APPS", []).append("newsroom.auth.saml")

    # drop mongodb now, indexes will be created during app init
    drop_mongo(cfg)

    app = get_app(config=cfg, testing=True)
    limiter_key = str(ObjectId())

    async def limiter_key_function():
        return limiter_key

    limiter.key_function = limiter_key_function

    async with app.app_context():
        await reset_elastic(app)
        cache.clean()
        app.init_indexes(True)
        yield app

    # Clean up blueprints, so they can be re-registered
    import importlib

    for name in app.config["BLUEPRINTS"]:
        mod = importlib.import_module(name)
        if getattr(mod, "blueprint"):
            mod.blueprint._got_registered_once = False


@fixture
def client(app: Quart):
    return app.test_client()


@fixture
def runner(app: Quart):
    """Necessary fixture to invoke click commands from unit tests"""
    return app.test_cli_runner()
