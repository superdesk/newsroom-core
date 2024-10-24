from . import oauth2
from superdesk.core.module import Module


module = Module(name="newsroom.auth_server.client", endpoints=[oauth2.blueprint], init=oauth2.config_oauth)
