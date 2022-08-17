from flask_script import Manager

from newsroom.web.factory import get_app


app = get_app()
manager = Manager(app)
