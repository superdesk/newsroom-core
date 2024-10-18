from superdesk.core.module import Module

from .views import blueprint

module = Module(name="newsroom.company_admin", endpoints=[blueprint])
