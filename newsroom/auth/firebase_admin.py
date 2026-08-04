import json
import logging

from typing import Any

from superdesk.core import get_app_config


logger = logging.getLogger(__name__)


class FirebasePasswordResetError(RuntimeError):
    pass


class FirebaseAdminConfigError(FirebasePasswordResetError):
    pass


class FirebaseUserNotFoundError(FirebasePasswordResetError):
    pass


def _build_credential(credentials_module: Any, config: Any):
    if isinstance(config, dict):
        config_value = (config.get("credentials_json") or config.get("credentials_path") or "").strip()
    elif isinstance(config, str):
        config_value = config.strip()
    else:
        config_value = ""

    if not config_value:
        return None

    if config_value.startswith("{"):
        try:
            return credentials_module.Certificate(json.loads(config_value))
        except json.JSONDecodeError as exc:
            raise FirebaseAdminConfigError("FIREBASE_ADMIN_CONFIG is not valid JSON") from exc

    return credentials_module.Certificate(config_value)


def _get_firebase_auth_client():
    try:
        import firebase_admin
        from firebase_admin import auth, credentials
    except ImportError as exc:
        raise FirebaseAdminConfigError("firebase-admin package is not installed") from exc

    config = get_app_config("FIREBASE_ADMIN_CONFIG")
    app_name = "newsroom"

    try:
        app = firebase_admin.get_app(app_name)
    except ValueError:
        init_kwargs: dict[str, Any] = {"name": app_name}
        credential = _build_credential(credentials, config)
        if credential is not None:
            init_kwargs["credential"] = credential

        project_id = (get_app_config("FIREBASE_CLIENT_CONFIG") or {}).get("projectId")
        if project_id:
            init_kwargs["options"] = {"projectId": project_id}

        app = firebase_admin.initialize_app(**init_kwargs)

    return auth, app


def update_firebase_password(email: str, password: str) -> str:
    auth, app = _get_firebase_auth_client()

    try:
        user = auth.get_user_by_email(email, app=app)
    except auth.UserNotFoundError as exc:
        raise FirebaseUserNotFoundError(f"No Firebase user found for {email}") from exc
    except Exception as exc:
        raise FirebasePasswordResetError(f"Could not load Firebase user for {email}") from exc

    try:
        auth.update_user(user.uid, password=password, app=app)
    except Exception as exc:
        raise FirebasePasswordResetError(f"Could not update Firebase password for {email}") from exc

    logger.info("Updated Firebase password for %s", email)
    return user.uid
