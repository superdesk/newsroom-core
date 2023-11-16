import abc

# from type

from newsroom.types import AuthProviderConfig, AuthProviderType


class AuthProviderFeatures(object):
    verify_email: bool
    change_password: bool

    def __init__(self, *, verify_email=False, change_password=False):
        self.verify_email = verify_email
        self.change_password = change_password

    def __iter__(self):
        """Needed for export to json for client."""
        return iter(
            [
                ("verify_email", self.verify_email),
                ("change_password", self.change_password),
            ]
        )


class AuthProvider(abc.ABC):
    type: AuthProviderType
    config: AuthProviderConfig
    features = AuthProviderFeatures()

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
    features = AuthProviderFeatures()


class SAMLAuthProvider(AuthProvider):
    type = AuthProviderType.SAML
    features = AuthProviderFeatures()


class FirebaseAuthProvider(AuthProvider):
    type = AuthProviderType.FIREBASE
    features = AuthProviderFeatures(change_password=True)
