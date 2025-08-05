# This file is part of Superdesk.
#
# Copyright 2019 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from typing import Any
import logging

from authlib.oauth2.rfc6749 import grants
from bson import ObjectId
from bson.errors import InvalidId

from superdesk.utc import utcnow

from superdesk.core.types import Request
from superdesk.auth_server.quart_oauth2 import OAuth2Server, OAuth2Client
from superdesk.flask import request as flask_request

from newsroom.oauth_clients.clients_async import ClientService

logger = logging.getLogger(__name__)


class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_basic", "client_secret_post"]


class NewshubOAuth2Server(OAuth2Server):
    grant_classes = [ClientCredentialsGrant]
    add_scope_to_jwt = False

    def query_client(self, client_id: str) -> OAuth2Client | None:
        try:
            client_data = ClientService().mongo.find_one({"_id": ObjectId(client_id)})
        except InvalidId as e:
            logger.error("Invalid 'client_id' was provided. Exception: {}".format(e))
            return None

        if client_data is None:
            return None

        return OAuth2Client(client_data, ClientCredentialsGrant.TOKEN_ENDPOINT_AUTH_METHODS)

    async def issue_token_endpoint(self, request: Request) -> Any:
        current_time = utcnow()
        try:
            token_response = await self.server.create_token_response()
            if flask_request.authorization:
                client_id = flask_request.authorization.get("username")
            else:
                client_id = (await request.get_form()).get("client_id")
        except Exception:
            raise
        else:
            if client_id:
                await ClientService().system_update(ObjectId(client_id), {"last_active": current_time})
            return token_response
