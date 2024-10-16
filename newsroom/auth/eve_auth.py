from eve.auth import BasicAuth


# TODO-ASYNC: Remove this once everything is async
class SessionAuth(BasicAuth):
    def authorized(self, allowed_roles, resource, method):
        from .utils import get_user_or_none_from_request

        user = get_user_or_none_from_request(None)
        if not user:
            return False
        elif not resource:
            return True  # list of apis is open

        return user.user_type in allowed_roles
