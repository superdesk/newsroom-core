import logging
from pathlib import Path

from superdesk.core import get_current_app
from apps.prepopulate.app_initialize import fillEnvironmentVariables

logger = logging.getLogger(__name__)


async def async_entity_import(entity_name, path, file_name, index_params, do_patch=False, force=False):
    """Custom import function for newsroom async entities"""
    logger.info("Process %r", entity_name)
    file_path = Path(path) / file_name
    app = get_current_app()

    if not file_path.exists():
        logger.info(" - file not exists: %s", file_path)
        return

    logger.info(" - got file path: %s", file_path)

    with file_path.open("rt", encoding="utf-8") as f:
        import json

        json_data = json.loads(f.read())

    data = [fillEnvironmentVariables(item) for item in json_data if fillEnvironmentVariables(item) is not None]

    # Use async service
    async_app = app.async_app
    service = async_app.resources.get_resource_service(entity_name)

    # Get existing data using service
    existing_data = []
    existing = [item.to_dict() async for item in service.get_all()]
    update_data = True
    if not do_patch and len(existing) > 0:
        logger.info(" - data already exists none will be loaded")
        update_data = False
    elif do_patch and len(existing) > 0:
        logger.info(" - data already exists it will be updated")

    if update_data:
        if do_patch:
            for item in existing:
                for loaded_item in data:
                    if "_id" in loaded_item and loaded_item["_id"] == item["_id"]:
                        data.remove(loaded_item)
                        if force or item.get("init_version", 0) < loaded_item.get("init_version", 0):
                            existing_data.append(loaded_item)

        if data:
            for item in data:
                if not item.get("_etag"):
                    item["_etag"] = "init"
            await service.create(data)

        if existing_data and do_patch:
            for item in existing_data:
                item["_etag"] = "init"
                await service.update(item["_id"], item)

    logger.info(" - file imported successfully: %s", file_name)

    if index_params:
        for index in index_params:
            crt_index = list(index) if isinstance(index, list) else index
            options = crt_index.pop() if isinstance(crt_index[-1], dict) and isinstance(index, list) else {}
            collection = app.data.mongo.pymongo(resource=entity_name).db[entity_name]
            options.setdefault("background", True)
            index_name = collection.create_index(crt_index, **options)
            logger.info(" - index: %s for collection %s created successfully.", index_name, entity_name)
