from newsroom.data_updates import (
    GenerateUpdate,
    Upgrade,
    get_data_updates_files,
    Downgrade,
)

from .manager import manager


@manager.option("-r", "--resource", dest="resource", required=True)
def data_generate_update(resource):
    cmd = GenerateUpdate()
    cmd.run(resource)


@manager.option(
    "-i",
    "--id",
    dest="data_update_id",
    required=False,
    choices=get_data_updates_files(strip_file_extension=True),
    help="Data update id to run last",
)
@manager.option(
    "-f",
    "--fake-init",
    dest="fake",
    required=False,
    action="store_true",
    help="Mark data updates as run without actually running them",
)
@manager.option(
    "-d",
    "--dry-run",
    dest="dry",
    required=False,
    action="store_true",
    help="Does not mark data updates as done. This can be useful for development.",
)
def data_upgrade(data_update_id=None, fake=False, dry=False):
    cmd = Upgrade()
    cmd.run(data_update_id, fake, dry)


@manager.option(
    "-i",
    "--id",
    dest="data_update_id",
    required=False,
    choices=get_data_updates_files(strip_file_extension=True),
    help="Data update id to run last",
)
@manager.option(
    "-f",
    "--fake-init",
    dest="fake",
    required=False,
    action="store_true",
    help="Mark data updates as run without actually running them",
)
@manager.option(
    "-d",
    "--dry-run",
    dest="dry",
    required=False,
    action="store_true",
    help="Does not mark data updates as done. This can be useful for development.",
)
def data_downgrade(data_update_id=None, fake=False, dry=False):
    cmd = Downgrade()
    cmd.run(data_update_id, fake, dry)
