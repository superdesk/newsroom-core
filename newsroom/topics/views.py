from bson import ObjectId
from pydantic import BaseModel, ValidationError

from superdesk.core import json, get_app_config
from superdesk.flask import abort, url_for, session
from superdesk.core.web import Request, Response

from newsroom.types import Topic
from newsroom.email import send_user_email
from newsroom.decorator import login_required
from newsroom.auth import get_user, get_user_id
from newsroom.topics.topics_async import get_user_topics as _get_user_topics, auto_enable_user_emails
from newsroom.utils import get_json_or_400, get_entity_or_404, response_from_validation
from newsroom.notifications import (
    push_user_notification,
    push_company_notification,
    save_user_notifications,
    UserNotification,
)
from .topics_async import topic_endpoints, TopicService, TopicResourceModel
from newsroom.users.service import UsersService


class RouteArguments(BaseModel):
    user_id: str = None
    topic_id: str = None


@topic_endpoints.endpoint("/users/<string:user_id>/topics", methods=["GET"])
@login_required
async def get_topics(args: RouteArguments, params: None, request: Request):
    """Returns list of followed topics of given user"""
    if session["user"] != str(args.user_id):
        abort(403)
    topics = await _get_user_topics(args.user_id)
    return Response({"_items": topics}, 200, ())


@topic_endpoints.endpoint("/users/<string:user_id>/topics", methods=["POST"])
@login_required
async def post_topic(args: RouteArguments, params: None, request: Request):
    """Creates a user topic"""
    user = get_user()

    if str(user["_id"]) != str(args.user_id):
        abort(403)

    topic = await get_json_or_400()

    topic.update(
        {"user": user["_id"], "company": user.get("company"), "_id": ObjectId(), "created_filter": topic.pop("created")}
    )

    for subscriber in topic.get("subscribers") or []:
        subscriber["user_id"] = ObjectId(subscriber["user_id"])

    try:
        data = TopicResourceModel.model_validate(topic)
    except ValidationError as error:
        return response_from_validation(error)

    ids = await TopicService().create([data])

    await auto_enable_user_emails(topic, {}, user)

    if topic.get("is_global"):
        push_company_notification("topic_created", user_id=str(user["_id"]))
    else:
        push_user_notification("topic_created")

    return Response({"success": True, "_id": ids[0]}, 201, ())


@topic_endpoints.endpoint("/topics/my_topics", methods=["GET"])
@login_required
async def get_list_my_topics(args: RouteArguments, params: None, request: Request):
    topics = await _get_user_topics(get_user_id())
    return Response(topics, 200, ())


@topic_endpoints.endpoint("/topics/<string:topic_id>", methods=["POST"])
@login_required
async def update_topic(args: RouteArguments, params: None, request: Request):
    """Updates a followed topic"""
    data = await get_json_or_400()
    current_user = get_user(required=True)
    original = await TopicService().find_by_id(args.topic_id)

    if not can_edit_topic(original, current_user):
        abort(403)

    updates: Topic = {
        "label": data.get("label"),
        "query": data.get("query"),
        "created": data.get("created"),
        "filter": data.get("filter"),
        "navigation": data.get("navigation"),
        "company": current_user.get("company"),
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

    try:
        await TopicService().update(args.topic_id, updates)
    except ValidationError as error:
        return response_from_validation(error)

    topic = await TopicService().find_by_id(args.topic_id)

    await auto_enable_user_emails(updates, original, current_user)

    if topic.is_global or updates.get("is_global", False) != original.is_global:
        push_company_notification("topics")
    else:
        push_user_notification("topics")

    return Response({"success": True}, 200, ())


@topic_endpoints.endpoint("/topics/<string:topic_id>", methods=["DELETE"])
@login_required
async def delete(args: RouteArguments, params: None, request: Request):
    """Deletes a followed topic by given id"""
    service = TopicService()
    current_user = get_user(required=True)
    original = await service.find_by_id(args.topic_id)

    if not await can_edit_topic(original, current_user):
        abort(403)

    await service.delete(original)

    if original.is_global:
        push_company_notification("topics")
    else:
        push_user_notification("topics")

    return Response({"success": True}, 200, ())


async def can_user_manage_topic(topic, user):
    """
    Checks if the topic can be managed by the provided user
    """
    return (
        topic.is_global
        and str(topic.company) == str(user.get("company"))
        and (user.get("user_type") == "administrator" or user.get("manage_company_topics"))
    )


async def can_edit_topic(topic, user):
    """
    Checks if the topic can be edited by the user
    """
    if topic and (str(topic.user) == str(user["_id"]) or str(user["_id"])):
        return True
    return await can_user_manage_topic(topic, user)


async def get_topic_url(topic):
    url_params = {}
    if topic.get("query"):
        url_params["q"] = topic.get("query")
    if topic.get("filter"):
        url_params["filter"] = json.dumps(topic.get("filter"))
    if topic.get("navigation"):
        url_params["navigation"] = json.dumps(topic.get("navigation"))
    if topic.get("created"):
        url_params["created"] = json.dumps(topic.get("created"))
    if topic.get("advanced"):
        url_params["advanced"] = json.dumps(topic["advanced"])

    section = topic.get("topic_type")
    return url_for(
        "wire.wire" if section == "wire" else f"{section}.index",
        _external=True,
        **url_params,
    )


@topic_endpoints.endpoint("/topic_share", methods=["POST"])
@login_required
async def share(args: RouteArguments, params: None, request: Request):
    current_user = get_user(required=True)
    data = await get_json_or_400()
    assert data.get("users")
    assert data.get("items")
    topic = get_entity_or_404(data.get("items")["_id"], "topics")
    for user_id in data["users"]:
        user_data = await UsersService().find_by_id(user_id)
        user = user_data.dict(by_alias=True, exclude_unset=True)
        if not user or not user.get("email"):
            continue

        topic_url = await get_topic_url(topic)
        save_user_notifications(
            [
                UserNotification(
                    user=user["_id"],
                    action="share",
                    resource="topic",
                    item=topic["_id"],
                    data=dict(
                        shared_by=dict(
                            _id=current_user["_id"],
                            first_name=current_user["first_name"],
                            last_name=current_user["last_name"],
                        ),
                        url=topic_url,
                    ),
                )
            ]
        )
        template_kwargs = {
            "recipient": user,
            "sender": current_user,
            "topic": topic,
            "url": topic_url,
            "message": data.get("message"),
            "app_name": get_app_config("SITE_NAME"),
        }
        await send_user_email(
            user,
            template="share_topic",
            template_kwargs=template_kwargs,
        )
    return Response({"success": True}, 201, ())
