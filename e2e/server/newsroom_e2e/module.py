import multiprocessing

from superdesk import get_resource_service
from superdesk.core import get_current_app
from superdesk.core.module import Module
from superdesk.core.web import endpoint, Request, Response
from superdesk.cache import cache
from superdesk.timer import timer

from newsroom.auth.utils import start_user_session
from newsroom.tests.db import drop_mongo, reset_elastic
from tests.core.utils import get_db_collection

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
    user = create_default_user()
    start_user_session(user, True)

    app = get_current_app()
    async with app.app_context():
        for entry in json.get("resources") or []:
            resource = entry.get("resource")
            items = entry.get("items") or []

            if entry.get("use_db_collection", False):
                db_collection = get_db_collection(resource)
                for item in items:
                    result = await db_collection.insert_one(item)
                    ids.append(result.inserted_id)
            elif entry.get("use_resource_service", True):
                service = get_resource_service(resource)
                for item in items:
                    app.data.mongo._mongotize(item, resource)
                    ids.extend(service.post([item]))
            else:
                for item in items:
                    app.data.mongo._mongotize(item, resource)
                    ids.extend(app.data.insert(resource, [item]))
    return Response(ids)


module = Module("newsroom_e2e", endpoints=[init_e2e_app, populate_resources])
