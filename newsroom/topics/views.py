from bson import ObjectId
from superdesk import get_resource_service
from flask import json, jsonify, abort, current_app as app, request, url_for
from flask_babel import gettext

from newsroom.topics import blueprint
from newsroom.topics.topics import get_user_topics as _get_user_topics
from newsroom.utils import find_one
from newsroom.auth import get_user, get_user_id
from newsroom.decorator import login_required
from newsroom.utils import get_json_or_400, get_entity_or_404
from newsroom.email import send_template_email
from newsroom.notifications import (
    push_user_notification,
    push_company_notification,
    save_user_notifications,
    UserNotification,
)


@blueprint.route("/users/<user_id>/topics", methods=["GET"])
@login_required
def get_user_topics(user_id):
    return jsonify(_get_user_topics(user_id)), 200


@blueprint.route("/topics/my_topics", methods=["GET"])
@login_required
def get_list_my_topics():
    return jsonify(_get_user_topics(get_user_id())), 200


@blueprint.route("/topics/<topic_id>", methods=["POST"])
@login_required
def update_topic(topic_id):
    """Updates a followed topic"""
    data = get_json_or_400()
    current_user = get_user(required=True)
    original = get_resource_service("topics").find_one(req=None, _id=ObjectId(topic_id))

    if not can_edit_topic(original, current_user):
        abort(403)

    # If notifications are enabled, check to see if user is configured to receive emails
    data.setdefault("subscribers", [])
    if str(current_user["_id"]) in data["subscribers"]:
        user = get_resource_service("users").find_one(req=None, _id=current_user["_id"])
        if not user.get("receive_email"):
            return "", gettext(
                "Please enable 'Receive notifications' option in your profile to receive topic notifications"
            )  # noqa

    updates = {
        "label": data.get("label"),
        "query": data.get("query"),
        "created": data.get("created"),
        "filter": data.get("filter"),
        "navigation": data.get("navigation"),
        "company": current_user.get("company"),
        "subscribers": [ObjectId(uid) for uid in data["subscribers"]],
        "is_global": data.get("is_global", False),
        "folder": data.get("folder", None),
    }

    if original and updates.get("is_global") != original.get("is_global"):
        # reset folder when going from company to user and vice versa
        updates["folder"] = None

    response = get_resource_service("topics").patch(id=ObjectId(topic_id), updates=updates)
    if response.get("is_global") or updates.get("is_global", False) != original.get("is_global", False):
        push_company_notification("topics")
    else:
        push_user_notification("topics")
    return jsonify({"success": True}), 200


@blueprint.route("/topics/<topic_id>", methods=["DELETE"])
@login_required
def delete(topic_id):
    """Deletes a followed topic by given id"""
    current_user = get_user(required=True)
    original = get_resource_service("topics").find_one(req=None, _id=ObjectId(topic_id))

    if not can_edit_topic(original, current_user):
        abort(403)

    get_resource_service("topics").delete_action({"_id": ObjectId(topic_id)})
    if original.get("is_global"):
        push_company_notification("topics")
    else:
        push_user_notification("topics")
    return jsonify({"success": True}), 200


@blueprint.route("/topics/<topic_id>/subscribe", methods=["POST", "DELETE"])
@login_required
def subscribe_to_topic(topic_id):
    current_user = get_user(required=True)
    topic = find_one("topics", _id=ObjectId(topic_id))

    if not is_user_or_company_topic(topic, current_user):
        abort(403)

    subscribers = topic.get("subscribers") or []
    currently_subscribed = current_user["_id"] in subscribers
    topic_updated = False
    if request.method == "POST" and not currently_subscribed:
        subscribers.append(current_user["_id"])
        topic_updated = True
    elif request.method == "DELETE" and currently_subscribed:
        subscribers = [subscriber for subscriber in subscribers if subscriber != current_user["_id"]]
        topic_updated = True

    if topic_updated:
        # Use the ``update`` method, so we don't update the ``version_creator`` field unnecessarily
        get_resource_service("topics").update(id=topic["_id"], updates={"subscribers": subscribers}, original=topic)

        push_company_notification("topics")

    return jsonify({"success": True}), 200


def can_user_manage_topic(topic, user):
    """
    Checks if the topic can be managed by the provided user
    """
    return (
        topic.get("is_global")
        and str(topic.get("company")) == str(user.get("company"))
        and (user.get("user_type") == "administrator" or user.get("manage_company_topics"))
    )


def can_edit_topic(topic, user):
    """
    Checks if the topic can be edited by the user
    """
    user_ids = [user.get("id") for user in topic.get("users") or []]
    if topic and (str(topic.get("user")) == str(user["_id"]) or str(user["_id"]) in user_ids):
        return True
    return can_user_manage_topic(topic, user)


def is_user_or_company_topic(topic, user):
    """Checks if the topic is owned by the user or global to the users company"""

    if topic.get("user") == user.get("_id"):
        return True
    elif topic.get("company") and topic.get("is_global", False):
        return user.get("company") == topic.get("company")
    return False


def get_topic_url(topic):
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


@blueprint.route("/topic_share", methods=["POST"])
@login_required
def share():
    current_user = get_user(required=True)
    data = get_json_or_400()
    assert data.get("users")
    assert data.get("items")
    topic = get_entity_or_404(data.get("items")["_id"], "topics")
    for user_id in data["users"]:
        user = get_resource_service("users").find_one(req=None, _id=user_id)
        if not user or not user.get("email"):
            continue

        topic_url = get_topic_url(topic)
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
            "app_name": app.config["SITE_NAME"],
        }
        send_template_email(
            to=[user["email"]],
            template="share_topic",
            template_kwargs=template_kwargs,
        )
    return jsonify(), 201
