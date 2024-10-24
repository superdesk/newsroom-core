# This file is part of Superdesk.
#
# Copyright 2019 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import time
import logging
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from authlib.jose import jwt
from bson import ObjectId

from .models import query_client, save_token
from superdesk.utc import utcnow

from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request
from superdesk.core.app import SuperdeskAsyncApp

from newsroom.oauth_clients.clients_async import ClientService

logger = logging.getLogger(__name__)

authorization = AuthorizationServer(query_client=query_client, save_token=save_token)


blueprint = EndpointGroup("auth_server", __name__)

TOKEN_ENDPOINT = "/api/auth_server/token"
shared_secret = None
expiration_delay = 0


@blueprint.endpoint(TOKEN_ENDPOINT, methods=["POST"], auth=False)
async def issue_token(request: Request):
    current_time = utcnow()
    try:
        token_response = authorization.create_token_response()
        if request.authorization:
            client_id = request.authorization.get("username")
        else:
            client_id = (await request.form).get("client_id")
    except Exception:
        raise
    else:
        if client_id:
            await ClientService().system_update(ObjectId(client_id), {"last_active": current_time})
        return token_response


def generate_jwt_token(client, grant_type, user, scope):
    header = {"alg": "HS256"}
    payload = {
        "iss": "Superdesk Auth Server",
        "iat": int(time.time()),
        "exp": int(time.time() + expiration_delay),
        "client_id": client.client_id,
    }
    return jwt.encode(header, payload, shared_secret)


def config_oauth(app: SuperdeskAsyncApp):
    global expiration_delay
    expiration_delay = app.wsgi.config["AUTH_SERVER_EXPIRATION_DELAY"]
    global shared_secret
    shared_secret = app.wsgi.config["AUTH_SERVER_SHARED_SECRET"]
    if not shared_secret.strip():
        logger.warning(
            "No shared secret set, please set it using AUTH_SERVER_SHARED_SECRET "
            "environment variable or setting. Authorisation server can't be used"
        )
        return

    app.wsgi.config["OAUTH2_ACCESS_TOKEN_GENERATOR"] = generate_jwt_token
    app.wsgi.config["OAUTH2_TOKEN_EXPIRES_IN"] = {"client_credentials": expiration_delay}
    authorization.init_app(app.wsgi)
    authorization.register_grant(ClientCredentialsGrant)


class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_basic", "client_secret_post"]
