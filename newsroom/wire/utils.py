from superdesk.core import get_current_async_app

from newsroom.auth.utils import get_user_id_from_request, is_from_request, get_current_request


def get_picture(item):
    if item["type"] == "picture":
        return item
    return item.get("associations", {}).get("featuremedia") or get_body_picture(item)


def get_body_picture(item):
    pictures = [assoc for assoc in item.get("associations", {}).values() if assoc and assoc.get("type") == "picture"]
    if pictures:
        return pictures[0]


def get_caption(picture):
    if picture:
        return picture.get("description_text") or picture.get("body_text")


async def update_action_list(items, action_list, force_insert=False, item_type="items"):
    """
    Stores user id into array of action_list of an item
    :param items: items to be updated
    :param action_list: field name of the list
    :param force_insert: inserts into list regardless of the http method
    :param item_type: either items or agenda as the collection
    :return:
    """
    user_id = get_user_id_from_request(None)
    if not user_id:
        return

    app = get_current_async_app()
    db = app.mongo.get_collection_async(item_type)
    elastic = app.elastic.get_client_async(item_type)

    insert = force_insert
    if not insert and is_from_request():
        insert = get_current_request().method == "POST"

    if insert:
        updates = {"$addToSet": {action_list: user_id}}
    else:
        updates = {"$pull": {action_list: user_id}}
    for item_id in items:
        result = await db.update_one({"_id": item_id}, updates)
        if result.modified_count:
            modified = await db.find_one({"_id": item_id})
            await elastic.update(item_id, {action_list: modified[action_list]})
