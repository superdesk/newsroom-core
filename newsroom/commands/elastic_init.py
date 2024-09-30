from newsroom.core import get_current_wsgi_app
from .cli import newsroom_cli


@newsroom_cli.register_async_command("elastic_init", with_appcontext=True)
async def elastic_init():
    """Init elastic index.

    It will create index and put mapping. It should run only once so locks are in place.
    Thus mongo must be already setup before running this.

    Example:
    ::

        $ python manage.py elastic_init

    """
    app = get_current_wsgi_app()
    await app.data.init_elastic(app)
