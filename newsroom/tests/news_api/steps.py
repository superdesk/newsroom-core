import json
import lxml.etree
from datetime import datetime, timedelta, timezone
import re
from urllib.parse import quote

from behave import when, then
from behave.api.async_step import async_run_until_complete

from superdesk.tests import set_placeholder
from superdesk.tests.steps import apply_placeholders, json_match, get_json_data


@when("we save API token")
def step_save_token(context):
    token = context.news_api_tokens.get("_id")
    context.headers.append(("Authorization", f"Token {token}"))
    set_placeholder(context, "API_TOKEN", token)
    return


@when("we remove API token")
def step_remove_token(context):
    context.headers[:] = [h for h in context.headers if h[0] != "Authorization"]


@when('we set header "{name}" to value "{value}"')
def step_set_header(context, name, value):
    context.headers.append((name, value))


@then("we get headers in response")
def step_assert_response_header(context):
    test_headers = json.loads(apply_placeholders(context, context.text))
    response_headers = context.response.headers
    headers_dict = {}

    for h in response_headers:
        headers_dict[h[0]] = h[1]

    for t_h in test_headers:
        json_match(t_h, headers_dict)


@then("we store NEXT_PAGE from HATEOAS")
@async_run_until_complete
async def step_store_next_page_from_response(context):
    data = await get_json_data(context.response)
    links = data.get("_links", {})
    next_link = links.get("next") or links.get("next_page")
    href = next_link.get("href") if next_link else None
    assert href, data
    set_placeholder(context, "NEXT_PAGE", href)


@then('we get "{text}" in text response')
@async_run_until_complete
async def we_get_text_in_response(context, text):
    async with context.app.test_request_context(context.app.config["URL_PREFIX"]):
        data = await context.response.get_data(as_text=True)
        assert text in data


@then('we "{get}" "{text}" in atom xml response')
@async_run_until_complete
async def we_get_text_in_atom_xml_response(context, get, text):
    async with context.app.test_request_context(context.app.config["URL_PREFIX"]):
        body = await context.response.get_data()
        tree = lxml.etree.fromstring(body)
        assert "{http://www.w3.org/2005/Atom}feed" == tree.tag
        body = await context.response.get_data(as_text=True)
        if get == "get":
            assert text in body, f"{text} not in {body}"
        else:
            assert text not in body, f"{text} found in {body}"


@then('we "{get}" "{text}" in rss xml response')
@async_run_until_complete
async def we_get_text_in_rss_xml_response(context, get, text):
    async with context.app.test_request_context(context.app.config["URL_PREFIX"]):
        body = await context.response.get_data()
        tree = lxml.etree.fromstring(body)
        assert "rss" == tree.tag, tree.tag
        body = await context.response.get_data(as_text=True)
        if get == "get":
            assert text in body, f"{text} not in {body}"
        else:
            assert text not in body, f"{text} found in {body}"


@then("we check feed href for {date} and {exclude}")
@async_run_until_complete
async def we_check_feed_href(context, date, exclude):
    data = await get_json_data(context.response)
    links = data.get("_links", {})
    next_link = links.get("next") or links.get("next_page")
    href = next_link.get("href") if next_link else None

    match = re.match(r"^#DATE(?:([+-])(\d+))?#$", date)
    if match:
        sign, days = match.groups()
        days_offset = int(days) if days else 0
        if sign == "-":
            days_offset = -days_offset

        target_date = datetime.now(timezone.utc) + timedelta(days=days_offset)
        expected_date = target_date.strftime("%Y-%m-%d")

    assert f"start_date={expected_date}" in href
    assert f"exclude_ids={quote(exclude)}" in href
