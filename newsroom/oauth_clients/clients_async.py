from content_api import MONGO_PREFIX
from typing import Optional, Annotated, List, Dict, Union
from superdesk.core.resources import ResourceModel, ResourceConfig, MongoResourceConfig
from superdesk.core.resources.service import AsyncResourceService
from superdesk.core.web import EndpointGroup
from pydantic import Field
import logging
from bson import ObjectId


class ClientResource(ResourceModel):
    id: Annotated[Union[str, ObjectId], Field(alias="_id")] = None
    name: str
    password: str
    last_active: Optional[str] = None
    etag: Annotated[Optional[str], Field(alias="_etag")] = None


class ClientService(AsyncResourceService[ClientResource]):
    """Service class for managing OAuthClient resources"""

    resource_name = "oauth_clients"

    async def get_all_client(self) -> List[Dict]:
        try:
            # Collect all items asynchronously
            clients = [client async for client in self.get_all()]

            # Convert clients to list of dictionaries
            return [item.dict(by_alias=True, exclude_unset=True) for item in clients]

        except Exception as e:
            logging.error(f"Error retrieving data from clients: {e}")
            return []


clients_model_config = ResourceConfig(
    name="oauth_clients",
    data_class=ClientResource,
    mongo=MongoResourceConfig(
        prefix=MONGO_PREFIX,
    ),
    elastic=None,
    service=ClientService,
)

clients_endpoints = EndpointGroup("oauth_clients", __name__)
