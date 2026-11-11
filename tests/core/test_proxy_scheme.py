from quart import Quart, url_for

from newsroom.factory.app import BaseNewsroomApp


async def test_configure_proxy_scheme_generates_https_url():
    app = Quart(__name__)
    app.config["CLIENT_URL"] = "https://newsroom.example.com"
    app.config["PROXY_FIX_TRUSTED_HOPS"] = 1
    BaseNewsroomApp.configure_proxy_scheme(app)

    @app.get("/reset_password/<token>")
    async def reset_password(token):
        return url_for("reset_password", token=token, _external=True)

    response = await app.test_client().get("/reset_password/token", headers={"X-Forwarded-Proto": "https"})

    assert response.status_code == 200
    assert await response.get_data(as_text=True) == "https://localhost/reset_password/token"
