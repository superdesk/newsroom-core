import abc

from typing import TypedDict

from newsroom.types import AuthProviderConfig, AuthProviderType


class AuthProviderFeatures(TypedDict):
    verify_email: bool
    change_password: bool


class AuthProvider(abc.ABC):
    type: AuthProviderType
    config: AuthProviderConfig
    features: AuthProviderFeatures

    def __init__(self, config: AuthProviderConfig):
        self._id = config["_id"]
        self.name = config["name"]
        self.config = config

    @classmethod
    def get_provider(cls, data: AuthProviderConfig):
        if data["auth_type"] == AuthProviderType.FIREBASE:
            return FirebaseAuthProvider(data)
        if data["auth_type"] == AuthProviderType.GOOGLE_OAUTH:
            return GoogleOauthAuthProvider(data)
        if data["auth_type"] == AuthProviderType.SAML:
            return SAMLAuthProvider(data)
        return PasswordAuthProvider(data)


class PasswordAuthProvider(AuthProvider):
    type = AuthProviderType.PASSWORD
    features = AuthProviderFeatures(verify_email=True, change_password=True)


class GoogleOauthAuthProvider(AuthProvider):
    type = AuthProviderType.GOOGLE_OAUTH
    features = AuthProviderFeatures(verify_email=False, change_password=False)


class SAMLAuthProvider(AuthProvider):
    type = AuthProviderType.SAML
    features = AuthProviderFeatures(verify_email=False, change_password=False)


class FirebaseAuthProvider(AuthProvider):
    type = AuthProviderType.FIREBASE
    features = AuthProviderFeatures(verify_email=False, change_password=True)
