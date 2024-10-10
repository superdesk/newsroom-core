from bson import ObjectId
from typing import Optional, List, Dict, Any, Union

from newsroom import MONGO_PREFIX
from newsroom.types import TopicResourceModel, UserResourceModel
from newsroom.exceptions import AuthorizationError
from newsroom.auth.utils import get_user_from_request

# from newsroom.signals import user_deleted

from newsroom.users.service import UsersService
from newsroom.core.resources.service import NewshubAsyncResourceService
from newsroom.types import User, Topic

from superdesk.core.web import EndpointGroup

# from superdesk.core.module import SuperdeskAsyncApp
from superdesk.core.resources import ResourceConfig, MongoResourceConfig, RestEndpointConfig, RestParentLink


class TopicService(NewshubAsyncResourceService[TopicResourceModel]):
    async def on_update(self, updates: Dict[str, Any], original: TopicResourceModel) -> None:
        await super().on_update(updates, original)
        # If ``is_global`` has been turned off, then remove all subscribers
        # except for the owner of the Topic
        if original.is_global and "is_global" in updates and not updates.get("is_global"):
            # First find the subscriber entry for the original user
            subscriber = next(
                (
                    subscriber
                    for subscriber in (updates.get("subscribers") or original.subscribers or [])
                    if subscriber.user_id == original.user
                ),
                None,
            )

            # Then construct new array with either subscriber found or empty list
            updates["subscribers"] = [subscriber] if subscriber is not None else []

        if updates.get("folder"):
            updates["folder"] = ObjectId(updates["folder"])

    async def on_updated(self, updates: Dict[str, Any], original: TopicResourceModel) -> None:
        await super().on_updated(updates, original)

        try:
            current_user = get_user_from_request(None)
            await auto_enable_user_emails(updates, original, current_user)
        except AuthorizationError:
            # No user currently logged in, could this be coming from a celery task?
            pass

    async def on_delete(self, doc: TopicResourceModel):
        await super().on_delete(doc)
        users = await UsersService().search(lookup={"dashboards.topic_ids": doc.id})
        async for user in users:
            updates = {"dashboards": user.dashboards.copy()}
            updated_dashboards = []

            for dashboard in updates["dashboards"]:
                dashboard_dict = dashboard.to_dict()
                # Remove the deleted topic id from topic_ids
                dashboard_dict["topic_ids"] = [
                    topic_id for topic_id in dashboard_dict["topic_ids"] if topic_id != doc.id
                ]
                updated_dashboards.append(dashboard_dict)

            updates["dashboards"] = updated_dashboards
            await UsersService().system_update(user.id, updates=updates)

    async def on_user_deleted(self, sender, user: User, **kwargs):
        """
        Handle the cleanup of user-related topics when a user is deleted.

        This function is tbriggered by the `user_deleted` signal

        """
        # delete user private topics
        await self.delete_many(lookup={"is_global": False, "user": user["_id"]})

        # remove user topic subscriptions from existing topics

        topics = await self.search(lookup={"subscribers.user_id": user["_id"]})

        user_object_id = ObjectId(user["_id"])

        async for topic in topics:
            updates = dict(
                subscribers=[s for s in topic.subscribers if s["user_id"] != user_object_id],
            )

            if topic.user == user_object_id:
                topic.user = None

            await self.update(topic.id, updates)

        # remove user as a topic creator for the rest
        user_topics = await self.search(lookup={"user": user["_id"]})
        async for topic in user_topics:
            await self.update(topic.id, {"user": None})


async def get_user_topics(user_id: Union[ObjectId, str, None]) -> List[Topic]:
    if not user_id:
        return []
    user = await UsersService().find_by_id(user_id)
    data = await TopicService().find(
        {
            "$or": [
                {"user": user.id},
                {"$and": [{"company": user.company}, {"is_global": True}]},
            ]
        }
    )
    return await data.to_list_raw()


async def get_topics_with_subscribers(topic_type: Optional[str] = None) -> List[Topic]:
    lookup: Dict[str, Any] = (
        {"subscribers": {"$exists": True, "$ne": []}}
        if topic_type is None
        else {
            "$and": [
                {"subscribers": {"$exists": True, "$ne": []}},
                {"topic_type": topic_type},
            ]
        }
    )

    mongo_cursor = await TopicService().search(lookup=lookup)

    return await mongo_cursor.to_list_raw()


async def get_user_id_to_topic_for_subscribers(
    notification_type: Optional[str] = None,
) -> Dict[ObjectId, Dict[ObjectId, Topic]]:
    user_topic_map: Dict[ObjectId, Dict[ObjectId, Topic]] = {}
    for topic in await get_topics_with_subscribers():
        for subscriber in topic.get("subscribers") or []:
            if notification_type is not None and subscriber.get("notification_type") != notification_type:
                continue
            user_topic_map.setdefault(subscriber["user_id"], {})
            user_topic_map[subscriber["user_id"]][topic["_id"]] = topic

    return user_topic_map


async def get_agenda_notification_topics_for_query_by_id(item, users):
    """
    Returns active topics for a given agenda item
    :param item: agenda item
    :param users: active users dict
    :return: list of topics
    """
    lookup = {
        "$and": [
            {"subscribers": {"$exists": True, "$ne": []}},
            {"topic_type": "agenda"},
            {"query": item["_id"]},
        ]
    }

    mongo_cursor = await TopicService().search(lookup=lookup)
    topics = await mongo_cursor.to_list_raw()

    # filter out the topics those belong to inactive users
    return [t for t in topics if users.get(str(t["user"]))]


async def auto_enable_user_emails(
    updates: Topic | dict[str, Any],
    original: TopicResourceModel | None,
    user: UserResourceModel,
):
    if not updates.get("subscribers"):
        return

    # If current user is already subscribed to this topic,
    # then no need to enable their email notifications
    if original:
        for subscriber in original.subscribers or []:
            if str(subscriber.user_id) == str(user.id):
                return  # User already subscribed, no need to enable emails

    user_newly_subscribed = False
    for subscriber_dict in updates.get("subscribers", []):
        if str(subscriber_dict.get("user_id")) == str(user.id):
            user_newly_subscribed = True
            break

    if not user_newly_subscribed:
        return

    # The current user subscribed to this topic in this update
    # Enable their email notifications now
    await UsersService().update(user.id, updates={"receive_email": True})


# TODO-ASYNC, need to wait for SDESK-7376

# async def init(app: SuperdeskAsyncApp):
#     user_deleted.connect(await TopicService().on_user_deleted)  # type: ignore


topic_resource_config = ResourceConfig(
    name="topics",
    data_class=TopicResourceModel,
    service=TopicService,
    mongo=MongoResourceConfig(prefix=MONGO_PREFIX),
    rest_endpoints=RestEndpointConfig(
        parent_links=[RestParentLink(resource_name="users", model_id_field="user")], url="topics"
    ),
)

topic_endpoints = EndpointGroup("topic", __name__)
