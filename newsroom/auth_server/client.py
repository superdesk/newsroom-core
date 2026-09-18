from superdesk.core.module import Module
from .oauth2 import NewshubOAuth2Server


authorization = NewshubOAuth2Server("/api/auth_server/token")

module = Module(name="newsroom.auth_server.client", init=authorization.init_app)
