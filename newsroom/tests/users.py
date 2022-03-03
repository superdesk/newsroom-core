from flask import url_for


ADMIN_USER_ID = '5cc94b99bc4316684dc7dc07'


def test_login_succeeds_for_admin(client):
    response = client.post(
        url_for('auth.login'),
        data={'email': 'admin@sourcefabric.org', 'password': 'admin'},
    )
    assert response.status_code == 302
