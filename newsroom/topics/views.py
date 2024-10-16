from bson import ObjectId
from typing import Optional
from pydantic import BaseModel

from superdesk.utc import utcnow
from superdesk.core import json, get_app_config
from superdesk.flask import url_for
from superdesk.core.types import Request, Response

from newsroom.types import Topic, TopicResourceModel, UserResourceModel, UserRole
from newsroom.email import send_user_email
from newsroom.auth import auth_rules

from .topics_async import get_user_topics, auto_enable_user_emails, topic_endpoints, TopicService

from newsroom.utils import get_json_or_400
from newsroom.notifications import push_user_notification, push_company_notification, save_user_notifications
from newsroom.users.service import UsersService


class RouteArguments(BaseModel):
    user_id: Optional[str] = None
    topic_id: Optional[str] = None


@topic_endpoints.endpoint(
    "/users/<string:user_id>/topics", methods=["GET"], auth=[auth_rules.url_arg_must_be_current_user("user_id")]
)
async def get_topics(args: RouteArguments, params: None, request: Request) -> Response:
    """Returns list of followed topics of given user"""
    topics = await get_user_topics(args.user_id)
    return Response({"_items": topics})


@topic_endpoints.endpoint(
    "/users/<string:user_id>/topics", methods=["POST"], auth=[auth_rules.url_arg_must_be_current_user("user_id")]
)
async def post_topic(request: Request) -> Response:
    """Creates a user topic"""

    topic = await get_json_or_400()
    topic.update(
        dict(
            user=request.user.id,
            company=request.user.company,
            # `_created` needs to be set otherwise there is a clash given `TopicResourceModel` and
            # the base `ResourceModel` both have the same member (`created`). Without this
            # `created_filter` does not get converted/saved
            _created=utcnow(),
        )
    )

    ids = await TopicService().create([topic])
    await auto_enable_user_emails(topic, None, request.user)

    if topic.get("is_global"):
        push_company_notification("topic_created", user_id=str(request.user.id))
    else:
        push_user_notification("topic_created")

    return Response({"success": True, "_id": ids[0]}, 201)


@topic_endpoints.endpoint("/topics/my_topics", methods=["GET"])
async def get_list_my_topics(request: Request) -> Response:
    topics = await get_user_topics(request.user.id)
    return Response(topics)


@topic_endpoints.endpoint("/topics/<string:topic_id>", methods=["POST"])
async def update_topic(args: RouteArguments, params: None, request: Request) -> Response:
    """Updates a followed topic"""
    data = await get_json_or_400()
    original = await TopicService().find_by_id(args.topic_id)

    if not can_edit_topic(original, request.user):
        await request.abort(403)

    updates: Topic = {
        "label": data.get("label"),
        "query": data.get("query"),
        "created": data.get("created"),
        "filter": data.get("filter"),
        "navigation": data.get("navigation"),
        "company": request.user.company,
        "subscribers": data.get("subscribers") or [],
        "is_global": data.get("is_global", False),
        "folder": data.get("folder", None),
        "advanced": data.get("advanced", None),
    }

    for subscriber in updates["subscribers"]:
        subscriber["user_id"] = ObjectId(subscriber["user_id"])

    if original and updates.get("is_global") != original.is_global and original.folder == updates.get("folder"):
        # reset folder when going from company to user and vice versa
        updates["folder"] = None

    await TopicService().update(args.topic_id, updates)

    topic = await TopicService().find_by_id(args.topic_id)

    await auto_enable_user_emails(updates, original, request.user)

    if topic.is_global or updates.get("is_global", False) != original.is_global:
        push_company_notification("topics")
    else:
        push_user_notification("topics")

    return Response({"success": True})


@topic_endpoints.endpoint("/topics/<string:topic_id>", methods=["DELETE"])
async def delete(args: RouteArguments, params: None, request: Request) -> Response:
    """Deletes a followed topic by given id"""
    service = TopicService()
    original = await service.find_by_id(args.topic_id)

    if not can_edit_topic(original, request.user):
        await request.abort(403)

    await service.delete(original)

    if original.is_global:
        push_company_notification("topics")
    else:
        push_user_notification("topics")

    return Response({"success": True})


def can_edit_topic(topic: TopicResourceModel, user: UserResourceModel) -> bool:
    """
    Checks if the topic can be edited by the user
    """
    return str(topic.user) == str(user.id) or (
        topic.is_global
        and str(topic.company) == str(user.company)
        and (user.user_type == UserRole.ADMINISTRATOR or user.manage_company_topics)
    )


def get_topic_url(topic: TopicResourceModel):
    url_params = {}
    if topic.query:
        url_params["q"] = topic.query
    if topic.filter:
        url_params["filter"] = json.dumps(topic.filter)
    if topic.navigation:
        url_params["navigation"] = json.dumps(topic.navigation)
    if topic.created_filter:
        url_params["created"] = json.dumps(topic.created_filter)
    if topic.advanced:
        url_params["advanced"] = json.dumps(topic.advanced)

    return url_for(
        "wire.wire" if topic.topic_type == "wire" else f"{topic.topic_type}.index",
        _external=True,
        **url_params,
    )


@topic_endpoints.endpoint("/topic_share", methods=["POST"])
async def share(request: Request) -> Response:
    data = await get_json_or_400()
    assert data.get("users")
    assert data.get("items")

    user_service = UsersService()
    topic = await TopicService().find_by_id(data.get("items")["_id"])
    if not topic:
        return await request.abort(404)

    for user_id in data["users"]:
        user = await user_service.find_by_id(user_id)
        if not user or not user.email:
            continue

        user_dict = user.to_dict()
        topic_url = get_topic_url(topic)
        await save_user_notifications(
            [
                dict(
                    user=user.id,
                    action="share",
                    resource="topic",
                    item=topic.id,
                    data=dict(
                        shared_by=dict(
                            _id=request.user.id,
                            first_name=request.user.first_name,
                            last_name=request.user.last_name,
                        ),
                        url=topic_url,
                    ),
                )
            ]
        )
        template_kwargs = {
            "recipient": user_dict,
            "sender": request.user.to_dict(),
            "topic": topic.to_dict(),
            "url": topic_url,
            "message": data.get("message"),
            "app_name": get_app_config("SITE_NAME"),
        }
        await send_user_email(
            user_dict,
            template="share_topic",
            template_kwargs=template_kwargs,
        )
    return Response({"success": True}, 201)
