
from newsroom.gettext import get_session_locale


def test_get_session_locale(app):
    with app.test_request_context("/test"):
        assert "en" == get_session_locale()
