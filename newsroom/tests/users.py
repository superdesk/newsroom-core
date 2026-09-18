from superdesk.flask import url_for


ADMIN_USER_ID = "5cc94b99bc4316684dc7dc07"
ADMIN_USER_EMAIL = "admin@sourcefabric.org"


async def test_login_succeeds_for_admin(client):
    response = await client.post(
        url_for("auth.login"),
        form={"email": ADMIN_USER_EMAIL, "password": "admin"},
    )
    assert response.status_code == 302, await response.get_data(as_text=True)
