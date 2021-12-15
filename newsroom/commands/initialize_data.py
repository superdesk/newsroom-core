import pathlib
import logging
import elasticsearch.exceptions

from collections import OrderedDict

from apps.prepopulate.app_initialize import AppInitializeWithDataCommand as _AppInitializeWithDataCommand

from .manager import app, manager


logger = logging.getLogger(__name__)

__entities__: OrderedDict = OrderedDict([
    ('users', ('users.json', [], False)),
    ('ui_config', ('ui_config.json', [], True)),
])


class AppInitializeWithDataCommand(_AppInitializeWithDataCommand):

    def run(self, entity_name=None, force=False, init_index_only=False):
        logger.info('Starting data initialization')

        data_paths = [path for path in [
            pathlib.Path(app.config["SERVER_PATH"]).resolve().joinpath("data"),
            pathlib.Path(__file__).resolve().parent.parent.joinpath("init_data"),
        ] if path.exists()]

        # create indexes in mongo
        app.init_indexes()
        # put mapping to elastic
        try:
            app.data.init_elastic(app)
        except elasticsearch.exceptions.TransportError as err:
            logger.error("Error when initializing elastic %s", err)

        if init_index_only:
            logger.info('Only indexes initialized.')
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
                logger.info('Exception loading entity %s', name)

        logger.info('Data import finished')
        return 0


@manager.option(
    '-n', '--entity_name', dest='entity_name', action='append', required=False,
    help='entity(ies) to initialize'
)
@manager.option(
    '-f', '--force', dest='force', action='store_true', required=False,
    help='if True, update item even if it has been modified by user'
)
@manager.option(
    '-i', '--init-index-only', dest='init_index_only', action='store_true', required=False,
    help='if True, it only initializes index only'
)
def initialize_data(entity_name=None, path=None, force=False, init_index_only=False):
    """Initialize application with predefined data for various entities.

    Loads predefined data (users, ui_config, etc..) for instance.
    Mostly used for to load initial data for production instances,

    Supported entities:
    ::

        users, ui_config

    If no --entity-name parameter is supplied, all the entities are inserted.

    Example:
    ::

        $ python manage.py initialize_data

    """
    cmd = AppInitializeWithDataCommand()
    cmd.run(
        entity_name=entity_name,
        force=force,
        init_index_only=init_index_only,
    )
