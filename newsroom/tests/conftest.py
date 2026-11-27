from typing import cast
from pathlib import Path
from pytest import fixture
from copy import deepcopy

from quart import Quart

from superdesk.cache import cache
from superdesk.tests import TestClient, setup
from superdesk.db import clean_dbs
from superdesk.tests.mocks.emails import MockEmailFactory

from newsroom.web.factory import get_app, NewsroomWebApp
from newsroom.tests import markers
from newsroom.tests.app import get_test_config, set_limiter_key_function


root = (Path(__file__).parent / "..").resolve()


async def _create_app(config: dict | None = None) -> NewsroomWebApp:
    config = get_test_config({
        **(config or {}),
        "CACHE_TYPE": "redis",  # required for some auth & cache tests
    })
    app_instance = await setup(config=config, app_factory=get_app)

    async with app_instance.app_context():
        cache.clean()
        setattr(app_instance, "_config_backup", deepcopy(app_instance.config))
        app_instance.test_client_class = TestClient

    return app_instance


@fixture(scope="module")
async def module_app(request):
    app_instance = await _create_app()
    async with app_instance.app_context():
        await clean_dbs(None, app_instance.async_app, init_indexes=True)
        yield app_instance

    # Clean up blueprints, so they can be re-registered
    import importlib

    for name in app_instance.config["BLUEPRINTS"]:
        mod = importlib.import_module(name)
        if getattr(mod, "blueprint"):
            mod.blueprint._got_registered_once = False


@fixture(scope="function")
async def app(request, module_app):
    active_markers = [mark.name for mark in request.node.own_markers]
    reset_app = markers.enable_saml.name in active_markers or markers.enable_google_login.name in active_markers

    if reset_app:
        config: dict = {}
        if markers.enable_saml.name in active_markers:
            config["INSTALLED_APPS"] = module_app.config.get("INSTALLED_APPS") or [] + ["newsroom.auth.saml"]
        if markers.enable_google_login.name in active_markers:
            config["FORCE_ENABLE_GOOGLE_OAUTH"] = True
        module_app = await _create_app(config)
    else:
        async with module_app.app_context():
            await clean_dbs(None, module_app.async_app, init_indexes=False)
            cache.clean()
            domain_config = module_app.config["DOMAIN"]
            module_app.config = deepcopy(getattr(module_app, "_config_backup"))
            module_app.config["DOMAIN"] = domain_config

    set_limiter_key_function()

    async with module_app.app_context():
        cast(MockEmailFactory, module_app.mail).reset()
        yield module_app

    if reset_app:
        module_app = await _create_app()


@fixture
def client(app: Quart):
    return app.test_client()


@fixture
def runner(app: Quart):
    """Necessary fixture to invoke click commands from unit tests"""
    return app.test_cli_runner()
