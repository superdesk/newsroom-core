import json
import lxml.etree

from behave import when, then
from wooper.general import get_body
from superdesk.tests import set_placeholder
from superdesk.tests.steps import apply_placeholders, json_match, get_json_data


@when('we save API token')
def step_save_token(context):
    context.headers.append(('Authorization', context.news_api_tokens.get('_id')))
    return


@when('we set header "{name}" to value "{value}"')
def step_set_header(context, name, value):
    context.headers.append((name, value))


@then('we get headers in response')
def step_assert_response_header(context):
    test_headers = json.loads(apply_placeholders(context, context.text))
    response_headers = context.response.headers
    headers_dict = {}

    for h in response_headers:
        headers_dict[h[0]] = h[1]

    for t_h in test_headers:
        json_match(t_h, headers_dict)


@then('we store NEXT_PAGE from HATEOAS')
def step_store_next_page_from_response(context):
    data = get_json_data(context.response)
    href = ((data.get('_links') or {}).get('next_page') or {}).get('href')
    assert href, data
    set_placeholder(context, 'NEXT_PAGE', href)


@then('we get "{text}" in text response')
def we_get_text_in_response(context, text):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        assert (isinstance(get_body(context.response), str))
        assert (text in get_body(context.response))


@then('we "{get}" "{text}" in atom xml response')
def we_get_text_in_atom_xml_response(context, get, text):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        assert (isinstance(get_body(context.response), str))
        tree = lxml.etree.fromstring(get_body(context.response).encode('utf-8'))
        assert '{http://www.w3.org/2005/Atom}feed' == tree.tag
        body = get_body(context.response)
        if get == 'get':
            assert (text in body), f"{text} not in {body}"
        else:
            assert (text not in body), f"{text} found in {body}"
