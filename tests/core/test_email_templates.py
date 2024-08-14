import pytest
from werkzeug.exceptions import BadRequest, NotFound

from superdesk import get_resource_service
from newsroom.email_templates import RESOURCE


async def test_email_template_find_one(app):
    service = get_resource_service(RESOURCE)

    template = service.find_one(req=None, _id="share_wire")
    assert template
    assert template["_id"] == "share_wire"
    assert template["subject"]["default"] == "From {{ app_name }}: {{ subject_name | safe }}"

    with pytest.raises(BadRequest):
        service.find_one(req=None, name="my_custom_template")

    with pytest.raises(NotFound):
        service.find_one(req=None, _id="my_custom_template")


async def test_default_subjects(app):
    app.data.insert(
        RESOURCE,
        [
            {
                "_id": "signup_request_email",
                "subject": {
                    "translations": {"fr_ca": "Canadian French signup request"},
                },
            }
        ],
    )
    service = get_resource_service(RESOURCE)

    assert await service.get_translated_subject("agenda_new_coverage_email") == "New coverage"
    assert await service.get_translated_subject("signup_request_email") == "A new Newshub signup request"


async def test_get_subject_translation(app):
    app.data.insert(
        RESOURCE,
        [
            {
                "_id": "signup_request_email",
                "subject": {
                    "default": "A new Newshub signup request",
                    "translations": {
                        "fr_ca": "This should be the Canadian French version",
                        "fi": "This should be the Finnish version",
                    },
                },
            }
        ],
    )
    service = get_resource_service(RESOURCE)

    subject = await service.get_translated_subject("signup_request_email")
    assert subject == "A new Newshub signup request"

    subject = await service.get_translated_subject("signup_request_email", "fr_ca")
    assert subject == "This should be the Canadian French version"

    subject = await service.get_translated_subject("signup_request_email", "fi")
    assert subject == "This should be the Finnish version"


async def test_subject_translation_falls_back_to_default(app):
    app.data.insert(
        RESOURCE,
        [
            {
                "_id": "signup_request_email",
                "subject": {
                    "default": "A new Newshub signup request",
                    "translations": {
                        "fr_ca": "This should be the Canadian French version",
                        "fi": "This should be the Finnish version",
                    },
                },
            }
        ],
    )
    service = get_resource_service(RESOURCE)

    subject = await service.get_translated_subject("signup_request_email")
    assert subject == "A new Newshub signup request"

    subject = await service.get_translated_subject("signup_request_email", "unknown_lang")
    assert subject == "A new Newshub signup request"


async def test_get_subject_translation_with_template_variables(app):
    app.data.insert(
        RESOURCE,
        [
            {
                "_id": "validate_account_email",
                "subject": {
                    "default": "{{ app_name }} account created",
                    "translations": {
                        "fr_ca": "{{ app_name }} Canadian French account created",
                        "fi": "{{ app_name }} Finnish account created",
                    },
                },
            }
        ],
    )
    service = get_resource_service(RESOURCE)

    subject = await service.get_translated_subject("validate_account_email", app_name="Sourcefabric Newshub")
    assert subject == "Sourcefabric Newshub account created"

    subject = await service.get_translated_subject("validate_account_email", "fr_ca", app_name="Sourcefabric Newshub")
    assert subject == "Sourcefabric Newshub Canadian French account created"

    subject = await service.get_translated_subject("validate_account_email", "fi", app_name="Sourcefabric Newshub")
    assert subject == "Sourcefabric Newshub Finnish account created"


async def test_get_subject_falls_back_to_default_on_render_error(app):
    app.data.insert(
        RESOURCE,
        [
            {
                "_id": "coverage_request_email",
                "subject": {
                    "default": "Coverage inquiry: {{ item.name or item.slugline }}",
                    "translations": {"fr_ca": "Canadian French Coverage inquiry: {{ 1 / 0 }}"},
                },
            }
        ],
    )
    service = get_resource_service(RESOURCE)

    subject = await service.get_translated_subject("coverage_request_email", item={"name": "Test Coverage"})
    assert subject == "Coverage inquiry: Test Coverage"

    subject = await service.get_translated_subject("coverage_request_email", "fr_ca", item={"name": "Test Coverage"})
    assert subject == "Coverage inquiry: Test Coverage"


async def test_get_from_mongo_returns_working_cursor(app):
    app.data.insert(
        RESOURCE,
        [
            {
                "_id": "coverage_request_email",
                "subject": {
                    "default": "Coverage inquiry: {{ item.name or item.slugline }}",
                    "translations": {"fr_ca": "Canadian French Coverage inquiry: {{ 1 / 0 }}"},
                },
            }
        ],
    )
    service = get_resource_service(RESOURCE)
    items = service.get_from_mongo(None, {})
    assert 1 == items.count()
    assert 1 == len(list(items))
