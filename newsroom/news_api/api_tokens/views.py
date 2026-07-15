import asyncio
import logging
import json
from functools import wraps

from quart_babel import gettext
from superdesk.flask import jsonify, request
from superdesk import get_resource_service
from superdesk.json_utils import loads
from content_api.errors import BadParameterValueError

from newsroom.utils import get_json_or_400
from newsroom.news_api.api_tokens import blueprint
from . import API_TOKENS
from newsroom.auth.utils import is_valid_session, get_user_from_request
from newsroom.exceptions import AuthorizationError

logger = logging.getLogger(__name__)


def admin_session_required(f):
    """
    Ensure that the request is from a legitimate session and admin user.
    :param f:
    :return:
    """

    @wraps(f)
    async def async_decorated_function(*args, **kwargs):
        if not await is_valid_session():
            raise AuthorizationError(403, gettext("Forbidden"), title=gettext("403. Forbidden"))
        user = get_user_from_request(None)
        if not user or not user.is_admin():
            raise AuthorizationError(403, gettext("Forbidden"), title=gettext("403. Forbidden"))
        return await f(*args, **kwargs)

    return async_decorated_function


@blueprint.route("/news_api_tokens", methods=["POST"])
@admin_session_required
async def create():
    try:
        data = loads(json.dumps(await get_json_or_400()))
        new_token = await asyncio.to_thread(get_resource_service(API_TOKENS).post, [data])
        return jsonify({"token": new_token[0]}), 201
    except BadParameterValueError:
        return jsonify({"error": "Bad request"}), 400


@blueprint.route("/news_api_tokens", methods=["PATCH"])
@admin_session_required
async def update():
    token = request.args.get("token")
    data = await get_json_or_400()
    updated_data = await asyncio.to_thread(get_resource_service(API_TOKENS).patch, token, data)
    return jsonify(updated_data), 200


@blueprint.route("/news_api_tokens", methods=["DELETE"])
@admin_session_required
async def delete():
    company = request.args.get("company")
    token = await asyncio.to_thread(get_resource_service(API_TOKENS).find_one, req=None, company=company)
    if token and token.get("token"):
        await asyncio.to_thread(get_resource_service(API_TOKENS).delete, {"_id": token["token"]})
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Not Found"}), 404


@blueprint.route("/news_api_tokens", methods=["GET"])
@admin_session_required
async def get():
    company = request.args.get("company")
    data = await asyncio.to_thread(get_resource_service(API_TOKENS).find_one, req=None, company=company)
    if data:
        return jsonify(data), 200
    else:
        return jsonify({"error": "Not Found"}), 404
