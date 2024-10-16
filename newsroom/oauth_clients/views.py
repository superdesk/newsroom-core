import re
import bcrypt
from typing import Optional

from quart_babel import gettext
from pydantic import BaseModel, ValidationError
from werkzeug.exceptions import NotFound

from superdesk.utils import gen_password
from superdesk.core.types import Request, Response
from superdesk.core.resources.fields import ObjectId
from superdesk.core.resources.validators import get_field_errors_from_pydantic_validation_error

from newsroom.auth import auth_rules
from newsroom.utils import get_json_or_400_async
from .clients_async import clients_endpoints, ClientService


async def get_settings_data():
    data = await ClientService().get_all_clients()
    return {
        "oauth_clients": data,
    }


class ClientSearchArgs(BaseModel):
    q: Optional[str] = None


class ClientArgs(BaseModel):
    client_id: ObjectId


@clients_endpoints.endpoint(
    "/oauth_clients/search",
    methods=["GET"],
    auth=[auth_rules.account_manager_only],
)
async def search(args: None, params: ClientSearchArgs, request: Request) -> Response:
    lookup = None
    if params.q:
        regex = re.compile(f".*{re.escape(params.q)}.*", re.IGNORECASE)
        lookup = {"name": regex}
    cursor = await ClientService().search(lookup)
    data = await cursor.to_list_raw()
    return Response(data)


@clients_endpoints.endpoint(
    "/oauth_clients/new",
    methods=["POST"],
    auth=[auth_rules.account_manager_only],
)
async def create(request: Request) -> Response:
    """
    Creates the client with given client id
    """
    client = await get_json_or_400_async(request)
    if not isinstance(client, dict):
        return await request.abort(400)

    password = gen_password()
    doc = {
        "_id": ObjectId(),
        "name": client.get("name"),
        "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
    }
    try:
        ids = await ClientService().create([doc])
    except ValidationError as error:
        return Response(
            {
                field: list(errors.values())[0]
                for field, errors in get_field_errors_from_pydantic_validation_error(error).items()
            },
            400,
            (),
        )

    return Response({"success": True, "_id": ids[0], "password": password}, 201)


@clients_endpoints.endpoint(
    "/oauth_clients/<string:client_id>",
    methods=["GET", "POST"],
    auth=[auth_rules.account_manager_only],
)
async def edit(args: ClientArgs, params: None, request: Request) -> Response:
    """
    Edits the client with given client id
    """
    service = ClientService()
    original = await service.find_by_id(args.client_id)
    if not original:
        raise NotFound(gettext("Client not found"))
    elif request.method == "GET":
        return Response(original)

    request_json = await get_json_or_400_async(request)
    if not isinstance(request_json, dict):
        return await request.abort(400)

    updates = {}
    updates["name"] = request_json.get("name")
    await service.update(args.client_id, updates)
    return Response({"success": True})


@clients_endpoints.endpoint(
    "/oauth_clients/<string:client_id>",
    methods=["DELETE"],
    auth=[auth_rules.admin_only],
)
async def delete(args: ClientArgs, params: None, request: Request) -> Response:
    """
    Deletes the client with given client id
    """
    service = ClientService()
    original = await service.find_by_id(args.client_id)

    if not original:
        raise NotFound(gettext("Client not found"))
    try:
        await service.delete(original)
    except Exception as e:
        return Response({"error": str(e)}, 400)
    return Response({"success": True})
