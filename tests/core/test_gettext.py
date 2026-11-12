from newsroom.gettext import get_session_locale


async def test_get_session_locale(app):
    async with app.app_context():
        assert "en" == get_session_locale()


async def test_login_page_renders_with_language_query_param(app):
    client = app.test_client()
    response = await client.get("/login?language=fr_CA")

    assert response.status_code == 200
    page = await response.get_data(as_text=True)
    assert 'id="formLogin"' in page
