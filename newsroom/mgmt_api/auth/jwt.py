from newsroom.auth_server.auth import JWTAuth


def get_auth_instance(**kwargs):
    return JWTAuth()
