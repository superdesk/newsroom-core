from superdesk.core.web import EndpointGroup
from superdesk.core.module import Module
from newsroom.auth import auth_rules
from superdesk.flask import render_template

blueprint = EndpointGroup("mgmt_api_docs", __name__)


@blueprint.endpoint("/apidocs", auth=[auth_rules.admin_only])
async def mgmt_api_docs():
    return await render_template("mgmt-apidocs.html")


module = Module("newsroom.mgmt_api.mgmt_api_docs", endpoints=[blueprint])
