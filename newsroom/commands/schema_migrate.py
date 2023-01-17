from flask import current_app as app
from superdesk.lock import lock, unlock
from superdesk.commands.rebuild_elastic_index import RebuildElasticIndex
from newsroom import SCHEMA_VERSIONS
from .manager import manager


VERSION_ID = "schema_version"


@manager.command
def schema_migrate(resource_name=None):
    """Migrate elastic schema if needed, should be triggered on every deploy.

    It compares versions of each resource set in code (latest) to ones stored
    in db and only updates resource schema if those are different.

    Current version is read from settings and fallbacks to newsroom.SCHEMA_VERSION[``resource``],
    so that you can avoid migration via settings file if needed.

    Example:
    ::

        $ python manage.py schema:migrate

    """

    lock_name = "schema_migrate"

    if not lock(lock_name, expire=1800):
        return

    try:
        for resource in ["wire", "agenda"]:
            _resource_schema_migrate(resource)
    finally:
        unlock(lock_name)


def _resource_schema_migrate(resource: str):
    resource_schema_version = get_schema_version(resource)
    newsroom_schema_version = app.config.get(f"{resource.upper()}_SCHEMA_VERSION", SCHEMA_VERSIONS.get(resource))

    if resource_schema_version < newsroom_schema_version:
        print(f"Update {resource} schema from version {resource_schema_version} to {newsroom_schema_version}")
        RebuildElasticIndex().run("items" if resource == "wire" else resource)
        set_schema_version(resource, newsroom_schema_version)
    else:
        print(f"Resource {resource} already at version {resource_schema_version}")


def _get_version_db():
    """Get db used for storing version information."""
    return app.data.mongo.pymongo().db["newsroom"]


def get_schema_version(resource: str) -> int:
    """Read app schema version from db."""
    db = _get_version_db()
    version = db.find_one({"_id": VERSION_ID})
    return version.get(f"{resource}_version", 0) if version else 0


def set_schema_version(resource: str, version: int):
    """Store app schema version to db."""

    db = _get_version_db()
    db.update_one({"_id": VERSION_ID}, {"$set": {f"{resource}_version": version}}, upsert=True)
