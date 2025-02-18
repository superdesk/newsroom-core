import json
from typing import Any

from behave import given, when
from newsroom.tests.steps import async_run_until_complete
from newsroom.tests.web_api.steps import get_json_data
from superdesk.tests.steps import (
    apply_placeholders,
    get_prefixed_url,
    get_res,
    get_resource_name,
    if_match,
    set_user_default,
)


@given("empty auth token")
def given_empty_auth_token(context: Any) -> None:
    """
    Removes the Authorization token from headers to simulate an unauthenticated request.

    :param context: Behave test context that contains request headers.
    """
    if not hasattr(context, "headers"):
        context.headers = []

    context.headers = [header for header in context.headers if header[0] != "Authorization"]


async def store_placeholder(context: Any, url: str) -> None:
    """
    Stores API response data in context if the response status is 200 or 201.

    :param context: Behave test context that contains API response data.
    :param url: The API endpoint URL.
    """
    if context.response.status_code in (200, 201):
        try:
            item = json.loads(await context.response.get_data())
            if item.get("_id"):
                resource_name = get_resource_name(url)
                setattr(context, resource_name, item)
                context.placeholders = getattr(context, "placeholders", {})
                context.placeholders[resource_name] = item
        except (ValueError, IndexError, KeyError):
            pass


@when('we post to this "{url}"')
@async_run_until_complete
async def step_impl_when_post_url(context: Any, url: str) -> dict[str, Any]:
    """
    Sends a POST request to the given URL with placeholder-applied data.

    :param context: Behave test context.
    :param url: API endpoint URL.
    :return: Parsed JSON response from the request.
    """
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
async def _step_impl_when_patch_url(context: Any, url: str) -> None:
    """
    Sends a PATCH request to update a resource at the given URL.

    :param context: Behave test context.
    :param url: API endpoint URL.
    """
    with context.app.mail.record_messages() as outbox:
        url = apply_placeholders(context, url)
        res = await get_res(url, context)
        headers = if_match(context, res.get("_etag"))
        data = apply_placeholders(context, context.text)
        href = get_prefixed_url(context.app, url)
        context.response = await context.client.patch(href, data=data, headers=headers)
        context.outbox = outbox
