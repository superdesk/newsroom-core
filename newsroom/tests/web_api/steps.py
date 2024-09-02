from behave import then, when, given
from behave.api.async_step import async_run_until_complete
from eve.methods.common import parse

from superdesk import get_resource_service
from superdesk.core import json
from superdesk.tests.steps import (
    assert_200,
    get_json_data,
    apply_placeholders,
    get_prefixed_url,
    set_placeholder,
    is_user_resource,
)
from newsroom.utils import deep_get


async def expect_status_in(response, codes):
    assert response.status_code in [
        int(code) for code in codes
    ], "exptected on of {expected}, got {code}, reason={reason}".format(
        code=response.status_code,
        expected=codes,
        reason=(await response.get_data()).decode("utf-8"),
    )


async def assert_ok(response):
    await expect_status_in(response, [200, 201])


@then("we get the following order")
@async_run_until_complete
async def step_impl_ordered_list(context):
    assert_200(context.response)
    response_data = ((await get_json_data(context.response)) or {}).get("_items")
    ids = [item["_id"] for item in response_data]
    expected_order = json.loads(context.text)

    assert ids == expected_order, "{} != {}".format(",".join(ids), ",".join(expected_order))


@when('we get json from "{url}"')
@async_run_until_complete
async def step_impl_get_json_array_from_url(context, url):
    url = apply_placeholders(context, url)
    async with context.app.test_request_context(url):
        context.response = await context.client.get(
            get_prefixed_url(context.app, url),
            headers=[header for header in context.headers if header[0] != "Content-Type"],
        )

    await assert_ok(context.response)


@when('we post form to "{url}"')
@async_run_until_complete
async def step_impl_when_post_form_to_url(context, url):
    url = apply_placeholders(context, url)
    data = json.loads(apply_placeholders(context, context.text))
    async with context.app.test_request_context(url):
        context.response = await context.client.post(
            get_prefixed_url(context.app, url),
            form={key: json.dumps(val) for key, val in data.items()},
            headers=[header for header in context.headers if header[0] != "Content-Type"],
        )

    await assert_ok(context.response)


@when('we post json to "{url}"')
@async_run_until_complete
async def step_impl_when_post_json_to_url(context, url):
    url = apply_placeholders(context, url)
    data = apply_placeholders(context, context.text)

    async with context.app.test_request_context(url):
        context.response = await context.client.post(url, data=data, headers=context.headers)

    await assert_ok(context.response)


@then('we store "{tag}" with item id')
@async_run_until_complete
async def step_impl_store_response_item_id(context, tag):
    data = await get_json_data(context.response)
    set_placeholder(context, tag, data.get("_id"))


@then("we get aggregations")
@async_run_until_complete
async def step_impl_get_aggregations(context):
    assert_200(context.response)
    response_aggs = ((await get_json_data(context.response)) or {}).get("_aggregations")
    expected_aggs = json.loads(context.text)

    for key, val in expected_aggs.items():
        agg_values = [bucket.get("key") for bucket in deep_get(response_aggs, key, {}).get("buckets") or {}]
        assert sorted(val) == sorted(agg_values), f"_aggregations['{key}']: {agg_values} != {val},\n{response_aggs}"


@when('we login with email "{email}" and password "{password}"')
@async_run_until_complete
async def when_we_login_as_user(context, email, password):
    async with context.app.test_request_context("/login"):
        await context.client.get(get_prefixed_url(context.app, "/logout"), headers=context.headers)
        response = await context.client.post(
            get_prefixed_url(context.app, "/login"),
            form=dict(
                email=email,
                password=password,
            ),
            headers=context.headers,
        )
        assert response.status_code == 302, response.status_code


@then("we get products assigned to items")
@async_run_until_complete
async def then_we_get_users_with_products(context):
    data = json.loads(apply_placeholders(context, context.text))
    list_items = await get_json_data(context.response)
    if not isinstance(list_items, list):
        list_items = [list_items]
    for user in list_items:
        user_id = str(user.get("_id"))
        user_data = data.get(user_id) or {}

        # Test company attribute matches
        if "company" in user_data:
            expected_company_id = user_data.get("company")
            actual_company_id = str(user.get("company"))
            assert expected_company_id == actual_company_id, (
                "company attribute does not match\n"
                f"expected_company_id: {expected_company_id}\n"
                f"actual_company_id: {actual_company_id}"
            )

        # Test products match
        if "products" in user_data:
            expected_product_ids = sorted(user_data.get("products") or [])
            actual_product_ids = sorted([str(product.get("_id")) for product in user.get("products") or []])
            assert actual_product_ids == expected_product_ids, (
                "products do not match\n"
                f"expected_product_ids: {expected_product_ids}\n"
                f"actual_product_ids: {actual_product_ids}"
            )

        # Test sections match
        if "sections" in user_data:
            expected_sections = user_data.get("sections") or []
            actual_sections = [name for name, value in (user.get("sections") or {}).items() if value]

            assert sorted(actual_sections) == sorted(expected_sections), (
                "sections do not match\n"
                f"expected_sections: {expected_sections}\n"
                f"actual_sections: {user.get('sections')}"
            )


@given('newsroom "{resource}"')
@async_run_until_complete
async def step_impl_given_newsroom_resource(context, resource):
    async with context.app.test_request_context(context.app.config["URL_PREFIX"]):
        if not is_user_resource(resource):
            get_resource_service(resource).delete_action()

        items = [parse(item, resource) for item in json.loads(context.text)]
        get_resource_service(resource).post(items)

        context.data = items
        context.resource = resource

        try:
            setattr(context, resource, items[-1])
        except KeyError:
            pass
