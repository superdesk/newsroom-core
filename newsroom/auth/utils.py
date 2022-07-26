import flask
import werkzeug
import superdesk

from typing import Optional
from flask_babel import _
from superdesk.utc import utcnow
from newsroom.users import UserData


def sign_user_by_email(
    email: str,
    redirect_on_success: str = "wire.index",
    redirect_on_error: str = "auth.login",
    create_missing: bool = False,
    userdata: Optional[UserData] = None,
) -> werkzeug.Response:
    users = superdesk.get_resource_service("users")
    user: UserData = users.find_one(req=None, email=email)

    if user is None and create_missing and userdata is not None:
        user = userdata.copy()
        user["is_enabled"] = True
        users.create([user])

    assert "_id" in user

    if user is None:
        flask.flash(_("User not found"), "danger")
        return flask.redirect(flask.url_for(redirect_on_error, user_error=1))

    users.system_update(
        user["_id"],
        {
            "is_validated": True,  # in case user was not validated before set it now
            "last_active": utcnow(),
        },
        user,
    )

    # Set flask session information
    flask.session["user"] = str(user["_id"])
    flask.session["name"] = "{} {}".format(
        user.get("first_name"), user.get("last_name")
    )
    flask.session["user_type"] = user["user_type"]

    return flask.redirect(flask.url_for(redirect_on_success))
