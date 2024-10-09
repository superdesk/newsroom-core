from superdesk.core.module import Module

from .views import push_endpoints

module = Module(name="newsroom.push", endpoints=[push_endpoints])
