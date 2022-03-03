from flask import url_for
from pytest import fixture
from bson import ObjectId


ADMIN_USER_ID = '5cc94b99bc4316684dc7dc07'


@fixture(autouse=True)
def init(app, setup):
    app.data.insert('users', [{
        '_id': ObjectId(ADMIN_USER_ID),
        'first_name': 'admin',
        'last_name': 'admin',
        'email': 'admin@sourcefabric.org',
        'password': '$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG',
        'user_type': 'administrator',
        'is_validated': True,
        'is_enabled': True,
        'is_approved': True,
        'receive_email': True,
    }])


def test_login_succeeds_for_admin(client):
    response = client.post(
        url_for('auth.login'),
        data={'email': 'admin@sourcefabric.org', 'password': 'admin'},
        follow_redirects=True
    )
    assert response.status_code == 200
