import time
from flask import current_app as app
from authlib.jose import jwt, JoseError

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
    header = {'alg': 'HS256'}
    payload = {
        "id": str(user["_id"]),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "user_type": user["user_type"],
        "exp": int(time.time()) + expiration,
    }

    return jwt.encode(header, payload, app.config["SECRET_KEY"]).decode('utf-8')



def verify_auth_token(token: str) -> Optional[AuthToken]:
    """
    Verifies and decodes the token
    :param token: Encoded token
    :return: decoded token as dict
    """
    try:
        decoded = jwt.decode(token, app.config["SECRET_KEY"])
        decoded.validate()

        return {
            "id": decoded["id"],
            "user_type": decoded["user_type"],
            "first_name": decoded["first_name"],
            "last_name": decoded["last_name"],
        }
    except (JoseError, KeyError):
        return None
