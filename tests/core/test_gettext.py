from newsroom.gettext import get_session_locale


async def test_get_session_locale(app):
    async with app.app_context():
        assert "en" == await get_session_locale()
