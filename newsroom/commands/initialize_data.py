import click
import pathlib
import logging
import elasticsearch.exceptions

from collections import OrderedDict

from flask import current_app
from flask.cli import with_appcontext

from apps.prepopulate.app_initialize import (
    AppInitializeWithDataCommand as _AppInitializeWithDataCommand,
)
from .cli import newsroom_cli

from .elastic_rebuild import elastic_rebuild


logger = logging.getLogger(__name__)

__entities__: OrderedDict = OrderedDict(
    [
        ("users", ("users.json", [], False)),
        ("ui_config", ("ui_config.json", [], True)),
        ("email_templates", ("email_templates.json", [], True)),
    ]
)


class AppInitializeWithDataCommand(_AppInitializeWithDataCommand):
    def run(self, entity_name=None, force=False, init_index_only=False):
        logger.info("Starting data initialization")
        app = current_app

        data_paths = [
            path
            for path in [
                pathlib.Path(app.config["SERVER_PATH"]).resolve().joinpath("data"),
                pathlib.Path(__file__).resolve().parent.parent.joinpath("init_data"),
            ]
            if path.exists()
        ]

        # create indexes in mongo
        app.init_indexes()
        # put mapping to elastic
        try:
            app.data.init_elastic(app)
        except elasticsearch.exceptions.TransportError as err:
            logger.error("Error when initializing elastic %s", err)

            if app.config.get("REBUILD_ELASTIC_ON_INIT_DATA_ERROR"):
                logger.warning("Can't update the mapping, running elastic_rebuild command now.")
                elastic_rebuild()
            else:
                logger.warning("Can't update the mapping, please run elastic_rebuild command.")

        if init_index_only:
            logger.info("Only indexes initialized.")
            return 0

        if entity_name is None:
            entity_name = list(__entities__.keys())
        elif isinstance(entity_name, str):
            entity_name = [entity_name]

        for name in entity_name:
            try:
                (file_name, index_params, do_patch) = __entities__[name]
                for path in data_paths:
                    if path.joinpath(file_name).exists():
                        self.import_file(name, path, file_name, index_params, do_patch, force)
                        break
            except KeyError:
                continue
            except Exception as ex:
                logger.exception(ex)
                logger.info("Exception loading entity %s", name)

        logger.info("Data import finished")
        return 0


@newsroom_cli.command("initialize_data")
@click.option(
    "-n",
    "--entity-name",
    multiple=True,
    required=False,
    help="entity(ies) to initialize",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    required=False,
    help="if True, update item even if it has been modified by user",
)
@click.option(
    "-i",
    "--init-index-only",
    is_flag=True,
    required=False,
    help="if True, it only initializes index only",
)
@with_appcontext
def initialize_data(entity_name, force, init_index_only):
    """Initialize application with predefined data for various entities.

    Loads predefined data (users, ui_config, email_templates, etc..) for instance.
    Mostly used for to load initial data for production instances,

    Supported entities:
    ::

        users, ui_config, email_templates

    If no --entity-name parameter is supplied, all the entities are inserted.

    Example:
    ::

        $ flask newsroom initialize_data

    """
    cmd = AppInitializeWithDataCommand()
    cmd.run(
        entity_name=entity_name,
        force=force,
        init_index_only=init_index_only,
    )
