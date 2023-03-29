import bcrypt
import newsroom

from typing import TypedDict
from flask import current_app as app, session, abort, request
from flask_babel import gettext
from werkzeug.exceptions import BadRequest

from newsroom.auth import get_user_id, get_user
from newsroom.utils import set_original_creator, set_version_creator
from superdesk.utils import is_hashed, get_hash
from newsroom.auth.utils import is_current_user_admin, is_current_user_account_mgr, is_current_user_company_admin
from newsroom.user_roles import UserRole
from newsroom.signals import user_created, user_updated, user_deleted


class UserData(TypedDict, total=False):
    _id: str
    email: str
    first_name: str
    last_name: str
    user_type: str
    company: str
    is_enabled: bool


class UsersResource(newsroom.Resource):
    """
    Users schema
    """

    schema = {
        "password": {"type": "string", "minlength": 8},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "email": {"unique": True, "type": "string", "required": True},
        "phone": {"type": "string", "nullable": True},
        "mobile": {"type": "string", "nullable": True},
        "role": {"type": "string", "nullable": True},
        "signup_details": {"type": "dict"},
        "country": {"type": "string"},
        "company": newsroom.Resource.rel("companies", embeddable=True, required=False),
        "user_type": {
            "type": "string",
            "allowed": [role.value for role in UserRole],
            "default": "public",
        },
        # user must have his auth method validated in order to login
        "is_validated": {"type": "boolean", "default": False},
        # user must be enabled in order to login
        "is_enabled": {"type": "boolean", "default": True},
        # flag if user was approved, applies to users who registers themselves,
        # they must be approved within predefined time otherwise they won't be
        # able to login
        "is_approved": {"type": "boolean", "default": False},
        "expiry_alert": {"type": "boolean", "default": False},
        "token": {
            "type": "string",
        },
        "token_expiry_date": {
            "type": "datetime",
        },
        "receive_email": {"type": "boolean", "default": True},
        "receive_app_notifications": {"type": "boolean", "default": True},
        "locale": {
            "type": "string",
        },
        "manage_company_topics": {"type": "boolean", "default": False},
        "last_active": {"type": "datetime", "required": False, "nullable": True},
        "original_creator": newsroom.Resource.rel("users"),
        "version_creator": newsroom.Resource.rel("users"),
        "products": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "_id": newsroom.Resource.rel("products"),
                    "section": {"type": "string", "default": "wire"},
                },
            },
        },
        "sections": {
            "type": "dict",
            "nullable": True,
        },
    }

    item_methods = ["GET", "PATCH", "PUT", "DELETE"]
    resource_methods = ["GET", "POST"]
    datasource = {
        "source": "users",
        "projection": {"password": 0},
        "default_sort": [("first_name", 1)],
    }
    mongo_indexes = {
        "email": (
            [("email", 1)],
            {"unique": True, "collation": {"locale": "en", "strength": 2}},
        )
    }


USER_PROFILE_UPDATES = {
    "locale",
    "first_name",
    "last_name",
    "phone",
    "mobile",
    "country",
    "receive_email",
    "receive_app_notifications",
    "role",
}


COMPANY_ADMIN_ALLOWED_UPDATES = USER_PROFILE_UPDATES.union(
    {
        "email",
        "products",
        "sections",
        "is_approved",
        "is_enabled",
        "expiry_alert",
        "manage_company_topics",
        "token",
        "token_expiry_date",
        # populated by system
        "_created",
        "_updated",
    }
)


class UsersService(newsroom.Service):
    """
    A service that knows how to perform CRUD operations on the `users`
    collection.

    Serves mainly as a proxy to the data layer.
    """

    def on_create(self, docs):
        super().on_create(docs)
        for doc in docs:
            self.check_permissions(doc)
            set_original_creator(doc)
            if doc.get("password", None) and not is_hashed(doc.get("password")):
                doc["password"] = self._get_password_hash(doc["password"])

    def on_created(self, docs):
        super().on_created(docs)
        for doc in docs:
            user_created.send(self, user=doc)

    def on_update(self, updates, original):
        self.check_permissions(original, updates)
        set_version_creator(updates)
        if "password" in updates:
            updates["password"] = self._get_password_hash(updates["password"])
        app.cache.delete(str(original.get("_id")))
        app.cache.delete(original.get("email"))

    def on_updated(self, updates, original):
        # set session locale if updating locale for current user
        if updates.get("locale") and original["_id"] == get_user_id() and updates["locale"] != original.get("locale"):
            session["locale"] = updates["locale"]
        updated = original.copy()
        updated.update(updates)
        user_updated.send(self, user=updated, updates=updates)

    def _get_password_hash(self, password):
        return get_hash(password, app.config.get("BCRYPT_GENSALT_WORK_FACTOR", 12))

    def password_match(self, password, hashed_password):
        """Return true if the given password matches the hashed password
        :param password: plain password
        :param hashed_password: hashed password
        """
        try:
            return hashed_password == bcrypt.hashpw(password, hashed_password)
        except Exception:
            return False

    def on_deleted(self, doc):
        app.cache.delete(str(doc.get("_id")))
        user_deleted.send(self, user=doc)

    def on_delete(self, doc):
        if doc.get("_id") == get_user_id():
            raise BadRequest(gettext("Can not delete current user"))
        user = self.find_one(req=None, _id=doc["_id"])
        self.check_permissions(user)
        super().on_delete(doc)

    def check_permissions(self, doc, updates=None):
        """Check if current user has permissions to edit user."""
        if not request or request.method == "GET":  # in behave there is test request context
            return

        if is_current_user_admin() or is_current_user_account_mgr():
            return

        # Only check against metadata that has changed from the original
        updated_fields = (
            []
            if updates is None
            else [field for field in updates.keys() if updates[field] != doc.get(field) and field != "id"]
        )

        if is_current_user_company_admin():
            manager = get_user()
            if doc.get("company") and doc["company"] == manager.get("company"):
                if not updated_fields or all([key in COMPANY_ADMIN_ALLOWED_UPDATES for key in updated_fields]):
                    return
                if request and request.method == "DELETE" and doc.get("_id") != manager.get("_id"):
                    return

        if request and request.url_rule and request.url_rule.rule:
            if request.url_rule.rule in ["/reset_password/<token>", "/token/<token_type>"]:
                return
            elif request.url_rule.rule == "/users/<_id>":
                if not updated_fields or all([key in USER_PROFILE_UPDATES for key in updated_fields]):
                    return
        abort(403)
