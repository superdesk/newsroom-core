from unittest.mock import patch


def test_password_reset(client, app):
    resp = client.get("/token/reset_password")
    assert 200 == resp.status_code, resp.get_data(as_text=True)

    with patch("newsroom.auth.utils.send_reset_password_email") as send_email_mock:
        resp = client.post("/token/reset_password", data={"email": "foo@bar.com"})
        assert 302 == resp.status_code
        send_email_mock.assert_called_once()
        user, token = send_email_mock.call_args.args

    assert user
    assert token

    resp = client.get(f"/reset_password/{token}")
    assert 200 == resp.status_code, resp.get_data(as_text=True)

    resp = client.post(f"/reset_password/{token}", data={"new_password": "newpassword", "new_password2": "newpassword"})
    assert 302 == resp.status_code, resp.get_data(as_text=True)
