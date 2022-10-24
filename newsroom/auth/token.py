from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired,
)
from flask import current_app as app

from typing import TypedDict, Optional


class AuthToken(TypedDict):
    id: str
    user_type: str
    first_name: str
    last_name: str


def generate_auth_token(user, expiration=3600) -> bytes:
    """
    Generates a secure token for the user
    :param user: user
    :param expiration: ttl in seconds
    :return: token as encoded string
    """
    s = Serializer(app.config["SECRET_KEY"], expires_in=expiration)
    return s.dumps(
        {
            "id": str(user["_id"]),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "user_type": user["user_type"],
        }
    )


def verify_auth_token(token: str) -> Optional[AuthToken]:
    """
    Verifies and decodes th token
    :param token: Encoded token
    :return: decoded token as dict
    """
    s = Serializer(app.config["SECRET_KEY"])
    try:
        parsed = s.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token

    return {
        "id": parsed["id"],
        "user_type": parsed["user_type"],
        "first_name": parsed["first_name"],
        "last_name": parsed["last_name"],
    }
