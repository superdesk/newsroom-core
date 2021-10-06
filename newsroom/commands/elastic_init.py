from .manager import app, manager


@manager.command
def elastic_init():
    """Init elastic index.

    It will create index and put mapping. It should run only once so locks are in place.
    Thus mongo must be already setup before running this.

    Example:
    ::

        $ python manage.py elastic_init

    """
    app.data.init_elastic(app)
