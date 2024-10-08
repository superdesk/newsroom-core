import click
from newsroom.data_updates import (
    GenerateUpdate,
    Upgrade,
    get_data_updates_files,
    Downgrade,
)

from .cli import newsroom_cli


@newsroom_cli.command("data_generate_update")
@click.option("-r", "--resource", required=True, help="The resource for which you want to generate the update")
async def data_generate_update(resource):
    cmd = GenerateUpdate()
    await cmd.run(resource)


@newsroom_cli.command("data_upgrade")
@click.option(
    "-i",
    "--id",
    "data_update_id",
    required=False,
    type=click.Choice(get_data_updates_files(strip_file_extension=True)),
    help="Data update id to run last",
)
@click.option(
    "-f",
    "--fake-init",
    "fake",
    is_flag=True,
    required=False,
    help="Mark data updates as run without actually running them",
)
@click.option(
    "-d",
    "--dry-run",
    "dry",
    is_flag=True,
    required=False,
    help="Does not mark data updates as done. This can be useful for development.",
)
async def data_upgrade(data_update_id=None, fake=False, dry=False):
    cmd = Upgrade()
    await cmd.run(data_update_id, fake, dry)


@newsroom_cli.command("data_downgrade")
@click.option(
    "-i",
    "--id",
    "data_update_id",
    required=False,
    type=click.Choice(get_data_updates_files(strip_file_extension=True)),
    help="Data update id to run last",
)
@click.option(
    "-f",
    "--fake-init",
    "fake",
    is_flag=True,
    required=False,
    help="Mark data updates as run without actually running them",
)
@click.option(
    "-d",
    "--dry-run",
    "dry",
    is_flag=True,
    required=False,
    help="Does not mark data updates as done. This can be useful for development.",
)
async def data_downgrade(data_update_id=None, fake=False, dry=False):
    cmd = Downgrade()
    await cmd.run(data_update_id, fake, dry)
