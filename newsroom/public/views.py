import flask

from werkzeug.utils import secure_filename
from newsroom.public import blueprint


@blueprint.route("/page/<path:template>")
def page(template):
    return flask.render_template("page-{template}.html".format(template=secure_filename(template)))
