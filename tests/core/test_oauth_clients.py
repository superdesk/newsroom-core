from flask import json
from newsroom.tests.users import test_login_succeeds_for_admin, init as user_init  # noqa
from superdesk import get_resource_service


def test_oauth_clients(client):
    test_login_succeeds_for_admin(client)
    # Register a new client
    response = client.post('/clients/new', data=json.dumps({
        'name': 'client1',
    }), content_type='application/json')

    assert response.status_code == 201
    oauth_client = get_resource_service('clients').find_one(req=None, name='client1')

    # Update an existing client
    response = client.post('/clients/{}'.format(str(oauth_client['_id'])), data=json.dumps({
        'name': 'client2'
    }), content_type='application/json')

    assert response.status_code == 200

    # Delete an existing client
    response = client.delete('/clients/{}'.format(str(oauth_client['_id'])))
    assert response.status_code == 200
