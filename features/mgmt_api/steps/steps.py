from newsroom.tests.steps import async_run_until_complete
from newsroom.tests.web_api.steps import get_json_data
import json
from superdesk.tests.steps import (
    get_resource_name,
    apply_placeholders,
    set_user_default,
    get_prefixed_url,
    get_res,
    if_match,
)
from behave import given, when


@given("empty auth token")
def given_empty_auth_token(context):
    """Removes the Authorization token from headers to simulate an unauthenticated request."""
    if not hasattr(context, "headers"):
        context.headers = []

    context.headers = [header for header in context.headers if header[0] != "Authorization"]


async def store_placeholder(context, url):
    if context.response.status_code in (200, 201):
        try:
            item = json.loads(await context.response.get_data())
        except ValueError:
            assert False, await context.response.get_data()
        if item.get("_id"):
            try:
                setattr(context, get_resource_name(url), item)
                context.placeholders = getattr(context, "placeholders", {})
                context.placeholders[get_resource_name(url)] = item
            except (IndexError, KeyError):
                pass


@when('we post to this "{url}"')
@async_run_until_complete
async def step_impl_when_post_url(context, url):
    with context.app.mail.record_messages() as outbox:
        data = apply_placeholders(context, context.text)
        url = apply_placeholders(context, url)
        set_user_default(url, data)
        context.response = await context.client.post(
            get_prefixed_url(context.app, url), data=data, headers=context.headers
        )
        item = await get_json_data(context.response)
        context.outbox = outbox
        await store_placeholder(context, url)
        return item


@when('we patch to this "{url}"')
@async_run_until_complete
async def _step_impl_when_patch_url(context, url):
    with context.app.mail.record_messages() as outbox:
        url = apply_placeholders(context, url)
        res = await get_res(url, context)
        headers = if_match(context, res.get("_etag"))
        data = apply_placeholders(context, context.text)
        href = get_prefixed_url(context.app, url)
        context.response = await context.client.patch(href, data=data, headers=headers)
        context.outbox = outbox
