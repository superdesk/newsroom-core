from bson import ObjectId
from typing import Optional
from pydantic import BaseModel

from superdesk.utc import utcnow
from superdesk.core import json, get_app_config
from superdesk.flask import url_for, session
from superdesk.core.web import Request, Response

from newsroom.types import Topic
from newsroom.email import send_user_email
from newsroom.decorator import login_required
from newsroom.auth import get_user, get_user_id
from newsroom.topics.topics_async import get_user_topics as _get_user_topics, auto_enable_user_emails
from newsroom.utils import get_json_or_400, get_entity_or_404
from newsroom.notifications import push_user_notification, push_company_notification, save_user_notifications
from .topics_async import topic_endpoints, TopicService
from newsroom.users.service import UsersService
from newsroom.users.utils import get_user_or_abort


class RouteArguments(BaseModel):
    user_id: Optional[str] = None
    topic_id: Optional[str] = None


@topic_endpoints.endpoint("/users/<string:user_id>/topics", methods=["GET"])
@login_required
async def get_topics(args: RouteArguments, params: None, request: Request):
    """Returns list of followed topics of given user"""
    if session["user"] != str(args.user_id):
        await request.abort(403)

    topics = await _get_user_topics(args.user_id)
    return Response({"_items": topics})


@topic_endpoints.endpoint("/users/<string:user_id>/topics", methods=["POST"])
@login_required
async def post_topic(args: RouteArguments, params: None, request: Request):
    """Creates a user topic"""
    current_user = await get_user_or_abort()

    if current_user:
        user_dict = current_user.to_dict()

    if not user_dict or str(user_dict["_id"]) != str(args.user_id):
        await request.abort(403)

    topic = await get_json_or_400()

    if user_dict:
        data = {
            "user": user_dict.get("_id"),
            "company": user_dict.get("company"),
            "_id": ObjectId(),
            "is_global": topic.get("is_global", False),
            # `_created` needs to be set otherwise there is a clash given `TopicResourceModel` and
            # the base `ResourceModel` both have the same member (`created`). Without this
            # `created_filter` does not get converted/saved
            "_created": utcnow(),
        }
        topic.update(data)

    for subscriber in topic.get("subscribers") or []:
        subscriber["user_id"] = ObjectId(subscriber["user_id"])

    ids = await TopicService().create([topic])

    await auto_enable_user_emails(topic, {}, user_dict)

    if user_dict and topic.get("is_global"):
        push_company_notification("topic_created", user_id=str(user_dict.get("_id")))
    else:
        push_user_notification("topic_created")

    return Response({"success": True, "_id": ids[0]}, 201)


@topic_endpoints.endpoint("/topics/my_topics", methods=["GET"])
@login_required
async def get_list_my_topics(args: RouteArguments, params: None, request: Request):
    topics = await _get_user_topics(get_user_id())
    return Response(topics)


@topic_endpoints.endpoint("/topics/<string:topic_id>", methods=["POST"])
@login_required
async def update_topic(args: RouteArguments, params: None, request: Request):
    """Updates a followed topic"""
    data = await get_json_or_400()

    current_user = await get_user_or_abort()

    if current_user:
        user_dict = current_user.to_dict()

    original = await TopicService().find_by_id(args.topic_id)

    if not user_dict or not await can_edit_topic(original, user_dict):
        await request.abort(403)

    updates: Topic = {
        "label": data.get("label"),
        "query": data.get("query"),
        "created": data.get("created"),
        "filter": data.get("filter"),
        "navigation": data.get("navigation"),
        "company": user_dict.get("company", None),
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

    await auto_enable_user_emails(updates, original, user_dict)

    if topic.is_global or updates.get("is_global", False) != original.is_global:
        push_company_notification("topics")
    else:
        push_user_notification("topics")

    return Response({"success": True})


@topic_endpoints.endpoint("/topics/<string:topic_id>", methods=["DELETE"])
@login_required
async def delete(args: RouteArguments, params: None, request: Request):
    """Deletes a followed topic by given id"""
    service = TopicService()
    current_user = get_user(required=True)
    original = await service.find_by_id(args.topic_id)

    if not await can_edit_topic(original, current_user):
        await request.abort(403)

    await service.delete(original)

    if original.is_global:
        push_company_notification("topics")
    else:
        push_user_notification("topics")

    return Response({"success": True})


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
    if topic and (str(topic.user) == str(user["_id"])):
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
        user = user_data.to_dict()
        if not user or not user.get("email"):
            continue

        topic_url = await get_topic_url(topic)
        if current_user:
            await save_user_notifications(
                [
                    dict(
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
    return Response({"success": True}, 201)
