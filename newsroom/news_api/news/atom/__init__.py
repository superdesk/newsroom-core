from superdesk.core.module import Module
from .views import atom_endpoints

module = Module(name="newsroom.news_api.atom", endpoints=[atom_endpoints])
