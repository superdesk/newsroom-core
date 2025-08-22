from typing import List
from pytz import utc
from bson import ObjectId
from pytest import fixture
from datetime import datetime, timedelta
from quart import url_for

from newsroom.types import Product, UserResourceModel, CompanyResource
from superdesk.utc import utcnow
from newsroom.tests.users import ADMIN_USER_ID, test_login_succeeds_for_admin
from .test_utils import create_entries_for

from . import markers


PUBLIC_USER_ID = ObjectId("59b4c5c61d41c8d736852fbf")
PUBLIC_USER_FIRSTNAME = "Foo"
PUBLIC_USER_LASTNAME = "Bar"
PUBLIC_USER_NAME = "{} {}".format(PUBLIC_USER_FIRSTNAME, PUBLIC_USER_LASTNAME)
PUBLIC_USER_EMAIL = "foo@bar.com"
TEST_USER_ID = ObjectId("5cc94454bc43165c045ffec9")
NEW_USER_ID = ObjectId("59b4c5c61d41c8d736852f44")
COMPANY_1_ID = ObjectId("6215cbf55fc14ebe18e175a5")
COMPANY_2_ID = ObjectId("6215ce6ed2943dec3725afde")
COMPANY_3_ID = ObjectId("6215ce6ed2943dec3725af3f")
PRODUCT_1_ID = ObjectId()
PRODUCT_2_ID = ObjectId()
PRODUCT_3_ID = ObjectId()
PRODUCT_ALL_AGENDA_ID = ObjectId()

ADMIN_USER_EMAIL = "admin@sourcefabric.org"


def get_markers(request):
    return [mark.name for mark in request.node.own_markers]


items = [
    {
        "_id": "tag:foo",
        "type": "text",
        "version": 2,
        "headline": "Amazon Is Opening More Bookstores",
        "slugline": "AMAZON-BOOKSTORE-OPENING",
        "body_html": "<p>New stores will open in DC and Austin in 2018.</p><p>Next line</p>",
        "firstcreated": "2017-11-27T08:00:57+0000",
        "versioncreated": datetime.now(),
        "service": [{"code": "a", "name": "Service A"}],
        "products": [{"code": "1", "name": "product-1"}, {"code": "3", "name": "product-3"}],
    },
    {
        "_id": "urn:localhost:weather",
        "type": "text",
        "version": 1,
        "headline": "Weather",
        "slugline": "WEATHER",
        "body_html": "<p>Weather report</p>",
        "ancestors": ["tag:weather", "tag:weather:old"],
        "firstcreated": datetime.now() - timedelta(days=5),
        "versioncreated": datetime.now().replace(hour=23, minute=55, second=10) - timedelta(days=5),
        "service": [{"code": "b", "name": "Service B"}],
        "products": [{"code": "2", "name": "product-2"}],
    },
    {
        "_id": "urn:localhost:flood",
        "type": "text",
        "version": 1,
        "headline": "Flood Waters",
        "slugline": "Disaster",
        "body_html": "<p>Water levels keep rising</p>",
        "firstcreated": datetime.now() - timedelta(days=5),
        "versioncreated": datetime.now().replace(hour=23, minute=55, second=20) - timedelta(days=5),
        "service": [{"code": "c", "name": "Service C"}],
        "products": [{"code": "7", "name": "product-7"}],
    },
    {
        "_id": "tag:weather",
        "type": "text",
        "version": 2,
        "nextversion": "urn:localhost:weather",
        "versioncreated": datetime.now() - timedelta(days=8),
        "source": "AAP",
    },
    {
        "_id": "tag:weather:old",
        "type": "text",
        "version": 2,
        "nextversion": "tag:weather",
        "versioncreated": datetime.now() - timedelta(days=10),
        "service": [{"code": "c", "name": "Service C"}],
    },
    {
        "_id": "tag:out-of-default-range",
        "type": "text",
        "version": 1,
        "versioncreated": datetime.now() - timedelta(days=365),
        "service": [{"code": "c", "name": "Service C"}],
    },
]

agenda_items = [
    {
        "type": "event",
        "guid": "urn:conference",
        "event_id": "urn:conference",
        "versioncreated": datetime(2018, 6, 27, 11, 12, 4, tzinfo=utc),
        "name": "Conference Planning",
        "slugline": "Prime Conference",
        "internal_note": "Internal message for event",
        "_created": "2018-06-27T11:12:07+0000",
        "dates": {
            "end": datetime(2018, 7, 20, 4, 0, 0, tzinfo=utc),
            "start": datetime(2018, 7, 20, 4, 0, 0, tzinfo=utc),
        },
        "event": {
            "definition_short": "Blah Blah",
            "pubstatus": "usable",
            "files": [{"media": "media", "name": "test.txt", "mimetype": "text/plain"}],
            "internal_note": "Internal message for event",
            "state": "scheduled",
        },
        "firstcreated": "2018-06-27T11:12:04+0000",
        "_current_version": 1,
        "files": [{"media": "media", "name": "test.txt", "mimetype": "text/plain"}],
        "definition_short": "Blah Blah",
        "state": "scheduled",
        "pubstatus": "usable",
        "planning_items": [
            {
                "versioncreated": "2018-06-27T11:07:17+0000",
                "planning_date": "2018-07-20T04:00:00+0000",
                # "expired": False,
                # "flags": {"marked_for_not_publication": False},
                "slugline": "Prime Conference",
                # "item_class": "plinat:newscoverage",
                "pubstatus": "usable",
                # "item_id": "urn:planning",
                "name": "Conference Planning",
                "_id": "urn:planning",
                "firstcreated": "2018-06-27T11:07:17+0000",
                "state": "draft",
                "guid": "urn:planning",
                "agendas": [],
                # "_current_version": 1,
                # "type": "planning",
                "internal_note": "Internal message for planning",
                "coverages": [
                    {
                        "firstcreated": "2018-06-27T11:07:17+0000",
                        "planning": {
                            "g2_content_type": "text",
                            "genre": [{"name": "Article", "qcode": "Article"}],
                            "ednote": "An editorial Note",
                            "keyword": ["Motoring"],
                            "scheduled": "2018-04-09T14:00:53.000Z",
                            "slugline": "Raiders",
                            "internal_note": "Internal message for coverage",
                        },
                        "workflow_status": "active",
                        "coverage_id": "urn:coverage",
                        "news_coverage_status": {
                            "label": "Planned",
                            "name": "coverage intended",
                            "qcode": "ncostat:int",
                        },
                    }
                ],
            }
        ],
        "coverages": [
            {
                "planning_id": "urn:planning",
                "coverage_id": "urn:coverage",
                "scheduled": "2018-04-09T14:00:53.000Z",
                "coverage_type": "text",
                "workflow_status": "active",
                "coverage_status": "coverage intended",
                "slugline": "Raiders",
                "genre": [{"name": "Article", "qcode": "Article"}],
            }
        ],
    },
    {
        "type": "planning",
        "guid": "urn:planning",
        "event_id": "urn:conference",
        "versioncreated": datetime(2018, 6, 27, 11, 12, 4, tzinfo=utc),
        "name": "Conference Planning",
        "slugline": "Prime Conference",
        "internal_note": "Internal message for agenda",
        "planning_items": [
            {
                "versioncreated": "2018-06-27T11:07:17+0000",
                "planning_date": "2018-07-20T04:00:00+0000",
                "expired": False,
                "flags": {"marked_for_not_publication": False},
                "slugline": "Prime Conference",
                "item_class": "plinat:newscoverage",
                "pubstatus": "usable",
                "item_id": "urn:planning",
                "name": "Conference Planning",
                "_id": "urn:planning",
                "firstcreated": "2018-06-27T11:07:17+0000",
                "state": "draft",
                "guid": "urn:planning",
                "agendas": [],
                "_current_version": 1,
                "type": "planning",
                "internal_note": "Internal message for planning",
                "coverages": [
                    {
                        "firstcreated": "2018-06-27T11:07:17+0000",
                        "planning": {
                            "g2_content_type": "text",
                            "genre": [{"name": "Article", "qcode": "Article"}],
                            "ednote": "An editorial Note",
                            "keyword": ["Motoring"],
                            "scheduled": "2018-04-09T14:00:53.000Z",
                            "slugline": "Raiders",
                            "internal_note": "Internal message for coverage",
                        },
                        "workflow_status": "active",
                        "coverage_id": "urn:coverage",
                        "news_coverage_status": {
                            "label": "Planned",
                            "name": "coverage intended",
                            "qcode": "ncostat:int",
                        },
                    }
                ],
            }
        ],
        "_created": "2018-06-27T11:12:07+0000",
        "coverages": [
            {
                "firstcreated": "2018-06-27T11:07:17+0000",
                "planning": {
                    "g2_content_type": "text",
                    "genre": [{"name": "Article", "qcode": "Article"}],
                    "ednote": "An editorial Note",
                    "keyword": ["Motoring"],
                    "scheduled": "2018-04-09T14:00:53.000Z",
                    "slugline": "Raiders",
                    "internal_note": "Internal message for coverage",
                },
                "workflow_status": "active",
                "coverage_id": "urn:coverage",
                "planning_id": "urn:planning",
                "news_coverage_status": {
                    "label": "Planned",
                    "name": "coverage intended",
                    "qcode": "ncostat:int",
                },
            }
        ],
        "planning_date": "2018-07-20T04:00:00+0000",
        "firstcreated": "2018-06-27T11:12:04+0000",
        "_current_version": 1,
        "headline": "test headline",
    },
]


@fixture(autouse=True)
async def init_items(request, app):
    if markers.skip_auto_wire_items.name not in get_markers(request):
        await create_entries_for("items", items)


@fixture(autouse=True)
async def init_agenda_items(request, app):
    if markers.skip_auto_agenda_items.name not in get_markers(request):
        await create_entries_for("agenda", agenda_items)


@fixture()
async def user(app):
    _user = {
        "_id": ObjectId(ADMIN_USER_ID),
        "first_name": "admin",
        "last_name": "admin",
        "email": ADMIN_USER_EMAIL,
        "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
        "user_type": "administrator",
        "is_validated": True,
        "is_enabled": True,
        "is_approved": True,
        "receive_email": True,
        "receive_app_notifications": True,
    }

    await create_entries_for("auth_user", [_user])

    _user["password"] = "admin"
    return _user


@fixture()
async def admin(user):
    return user


@fixture()
async def auth_users(client, user):
    await test_login_succeeds_for_admin(client)


@fixture(autouse=True)
async def init_auth(app, auth_users):
    return


async def setup_user_company(app):
    await create_entries_for(
        "companies",
        [
            {
                "_id": COMPANY_1_ID,
                "sd_subscriber_id": "12345",
                "name": "Press Co.",
                "is_enabled": True,
                "contact_name": "Tom",
                "sections": {
                    "wire": True,
                    "agenda": True,
                },
                "products": [
                    {"_id": PRODUCT_1_ID, "section": "wire", "seats": 0},
                    {"_id": PRODUCT_2_ID, "section": "wire", "seats": 0},
                    {"_id": PRODUCT_3_ID, "section": "wire", "seats": 0},
                    {"_id": PRODUCT_ALL_AGENDA_ID, "section": "agenda", "seats": 0},
                ],
            },
            {
                "_id": COMPANY_2_ID,
                "name": "Paper Co.",
                "is_enabled": True,
            },
            {
                "_id": COMPANY_3_ID,
                "sd_subscriber_id": "12345",
                "name": "News Co.",
                "is_enabled": True,
                "contact_name": "Ketan",
                "restrict_coverage_info": True,
            },
        ],
    )

    await create_entries_for(
        "auth_user",
        [
            {
                "_id": PUBLIC_USER_ID,
                "user_type": "public",
                "email": PUBLIC_USER_EMAIL,
                "first_name": PUBLIC_USER_FIRSTNAME,
                "last_name": PUBLIC_USER_LASTNAME,
                "company": COMPANY_1_ID,
                "is_enabled": True,
                "is_approved": True,
                "_created": utcnow(),
                "receive_email": True,
                "receive_app_notifications": True,
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "manage_company_topics": False,
            },
            {
                "_id": TEST_USER_ID,
                "user_type": "public",
                "email": "test@bar.com",
                "first_name": "Test",
                "last_name": "Bar",
                "company": COMPANY_1_ID,
                "is_enabled": True,
                "is_approved": True,
                "_created": utcnow(),
                "receive_email": True,
                "receive_app_notifications": True,
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "manage_company_topics": False,
            },
            {
                "_id": NEW_USER_ID,
                "user_type": "administrator",
                "email": "restrict@user.com",
                "first_name": "Restrict",
                "last_name": "User",
                "company": COMPANY_3_ID,
                "is_enabled": True,
                "is_approved": True,
                "_created": utcnow(),
                "receive_email": True,
                "receive_app_notifications": True,
                "password": "$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG",
                "manage_company_topics": False,
            },
        ],
    )


@fixture(autouse=True)
async def init_company(app):
    await setup_user_company(app)


@fixture
async def public_company(app, init_company):
    company = await CompanyResource.get_service().find_by_id(COMPANY_1_ID)
    return None if company is None else company.to_dict()


@fixture
async def public_user(app, init_company):
    user = await UserResourceModel.get_service().find_by_id(PUBLIC_USER_ID)
    return None if user is None else user.to_dict()


@fixture
async def anonymous_user(client):
    await client.get(url_for("auth.logout"))


@fixture
async def restrict_user(app, init_company):
    user = await UserResourceModel.get_service().find_by_id(NEW_USER_ID)
    return None if user is None else user.to_dict()


@fixture
async def company_products(app):
    _products: List[Product] = [
        {
            "_id": PRODUCT_1_ID,
            "name": "product test",
            "query": "headline:more",
            "is_enabled": True,
            "product_type": "wire",
        },
        {
            "_id": PRODUCT_2_ID,
            "name": "product test 2",
            "query": "headline:Weather",
            "is_enabled": True,
            "product_type": "wire",
        },
        {
            "_id": PRODUCT_3_ID,
            "name": "all content",
            "query": "*:*",
            "is_enabled": True,
            "product_type": "wire",
        },
        {
            "_id": PRODUCT_ALL_AGENDA_ID,
            "name": "all agenda",
            "query": "*:*",
            "is_enabled": True,
            "product_type": "agenda",
        },
    ]

    await create_entries_for("products", _products)

    return _products
