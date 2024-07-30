import logging
from pydantic import Field
from datetime import datetime
from typing import Optional, Annotated, List, Dict


from superdesk.core.resources import ResourceModel, ResourceConfig, MongoResourceConfig, validators
from superdesk.core.resources.service import AsyncResourceService
from superdesk.core.web import EndpointGroup


from content_api import MONGO_PREFIX


class ClientResource(ResourceModel):
    name: Annotated[
        Optional[str],
        validators.validate_iunique_value_async(resource_name="oauth_clients", field_name="name"),
    ]
    password: str
    last_active: Optional[datetime] = None
    etag: Annotated[Optional[str], Field(alias="_etag")] = None


class ClientService(AsyncResourceService[ClientResource]):
    """Service class for managing OAuthClient resources"""

    resource_name = "oauth_clients"

    async def get_all_clients(self) -> List[Dict]:
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
