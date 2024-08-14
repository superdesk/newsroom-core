import re
import bcrypt
from typing import Optional

from quart_babel import gettext
from pydantic import BaseModel
from werkzeug.exceptions import NotFound

from superdesk.utils import gen_password
from superdesk.core.web import Request, Response
from superdesk.core.resources.fields import ObjectId

from newsroom.utils import get_json_or_400_async
from newsroom.decorator import admin_only, account_manager_only
from .clients_async import clients_endpoints, ClientService, ClientResource


async def get_settings_data():
    data = await ClientService().get_all_clients()
    return {
        "oauth_clients": data,
    }


class ClientSearchArgs(BaseModel):
    q: Optional[str] = None


class ClientArgs(BaseModel):
    client_id: ObjectId


@clients_endpoints.endpoint("/oauth_clients/search", methods=["GET"])
@account_manager_only
async def search(args: None, params: ClientSearchArgs, request: Request) -> Response:
    lookup = None
    if params.q:
        regex = re.compile(f".*{re.escape(params.q)}.*", re.IGNORECASE)
        lookup = {"name": regex}
    cursor = await ClientService().search(lookup)
    data = await cursor.to_list_raw()
    return Response(data, 200, ())


@clients_endpoints.endpoint("/oauth_clients/new", methods=["POST"])
@account_manager_only
async def create(request: Request) -> Response:
    """
    Creates the client with given client id
    """
    client = await get_json_or_400_async(request)
    if not isinstance(client, dict):
        return request.abort(400)

    password = gen_password()
    doc = {
        "_id": ObjectId(),
        "name": client.get("name"),
        "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
    }
    new_client = ClientResource.model_validate(doc)
    ids = await ClientService().create([new_client])
    return Response({"success": True, "_id": ids[0], "password": password}, 201, ())


@clients_endpoints.endpoint("/oauth_clients/<string:client_id>", methods=["GET", "POST"])
@account_manager_only
async def edit(args: ClientArgs, params: None, request: Request) -> Response:
    """
    Edits the client with given client id
    """
    service = ClientService()
    original = await service.find_by_id(args.client_id)
    if not original:
        return NotFound(gettext("Client not found"))
    elif request.method == "GET":
        return Response(original, 200, ())

    request_json = await get_json_or_400_async(request)
    if not isinstance(request_json, dict):
        return request.abort(400)

    updates = {}
    updates["name"] = request_json.get("name")
    await service.update(args.client_id, updates)
    return Response({"success": True}, 200, ())


@clients_endpoints.endpoint("/oauth_clients/<string:client_id>", methods=["DELETE"])
@admin_only
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
        return Response({"error": str(e)}, 400, ())
    return Response({"success": True}, 200, ())
