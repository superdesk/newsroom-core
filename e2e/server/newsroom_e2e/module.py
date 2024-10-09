import multiprocessing

from superdesk.core import get_current_app
from superdesk.core.module import Module
from superdesk.core.web import endpoint, Request, Response
from superdesk.cache import cache
from superdesk.timer import timer

from newsroom.auth.utils import start_user_session
from newsroom.tests.db import drop_mongo, reset_elastic
from tests.core.utils import create_entries_for

from .utils import create_default_user


@endpoint("e2e/init", methods=["POST"])
async def init_e2e_app(_request: Request) -> Response:
    with multiprocessing.Lock(), timer("app_init"):
        await reset_dbs()
        create_default_user()

    return Response("OK")


async def reset_dbs():
    app = get_current_app()
    drop_mongo(app.config)

    async with app.app_context():
        await reset_elastic(app)
        cache.clean()
        app.init_indexes()


@endpoint("e2e/populate_resources", methods=["POST"])
async def populate_resources(request: Request) -> Response:
    json = await request.get_json()
    ids = []
    user = await create_default_user()
    start_user_session(user, True)

    app = get_current_app()
    async with app.app_context():
        for entry in json.get("resources") or []:
            resource = entry.get("resource")
            items = entry.get("items") or []

            if entry.get("use_resource_service", True):
                ids.extend(await create_entries_for(resource, items))
            else:
                for item in items:
                    app.data.mongo._mongotize(item, resource)
                    ids.extend(app.data.insert(resource, [item]))
    return Response(ids)


module = Module("newsroom_e2e", endpoints=[init_e2e_app, populate_resources])
