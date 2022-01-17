from flask import json
from newsroom.tests.users import test_login_succeeds_for_admin, init as user_init  # noqa
from superdesk import get_resource_service


def test_oauth_clients(client):
    test_login_succeeds_for_admin(client)
    # Register a new company
    response = client.post('/clients/new', data=json.dumps({
        'name': 'client1',
    }), content_type='application/json')

    assert response.status_code == 201
    company = get_resource_service('clients').find_one(req=None, name='client1')
    
    # Update an existing company
    response = client.post('/clients/{}'.format(str(company['_id'])), data=json.dumps({
        'name': 'client2'
    }), content_type='application/json')

    assert response.status_code == 200

    # Delete an existing company
    response = client.delete('/clients/{}'.format(str(company['_id'])))
    assert response.status_code == 200
