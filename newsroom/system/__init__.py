from superdesk.core.module import Module

from .health import health_endpoints

module = Module(name="newsroom.system", endpoints=[health_endpoints])
