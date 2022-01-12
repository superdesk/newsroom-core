import re

import flask
from bson import ObjectId
import bcrypt
from flask import jsonify, current_app as app
from flask_babel import gettext
from superdesk import get_resource_service
from werkzeug.exceptions import NotFound

from newsroom.decorator import admin_only, account_manager_only
from newsroom.clients import blueprint
from newsroom.utils import query_resource, find_one, get_json_or_400
from superdesk.utils import gen_password


def get_settings_data():
    return {
        'clients': list(query_resource('clients')),
    }


@blueprint.route('/clients/search', methods=['GET'])
@account_manager_only
def search():
    lookup = None
    if flask.request.args.get('q'):
        regex = re.compile('.*{}.*'.format(flask.request.args.get('q')), re.IGNORECASE)
        lookup = {'name': regex}
    companies = list(query_resource('clients', lookup=lookup))
    return jsonify(companies), 200


@blueprint.route('/clients/new', methods=['POST'])
@account_manager_only
def create():
    """
    Creates the client with given client
    """
    client = get_json_or_400()

    password = gen_password()
    new_company = {
        'name': client.get('name'),
        'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    }

    ids = get_resource_service('clients').post([new_company])
    return jsonify({'success': True, '_id': ids[0], 'password': password}), 201


@blueprint.route('/clients/<_id>', methods=['GET', 'POST'])
@account_manager_only
def edit(_id):
    """
    Edits the client with given client id
    """
    client = find_one('clients', _id=ObjectId(_id))

    if not client:
        return NotFound(gettext('Client not found'))

    if flask.request.method == 'POST':
        client = get_json_or_400()
        updates = {}
        updates['name'] = client.get('name')
        get_resource_service('clients').patch(ObjectId(_id), updates=updates)
        app.cache.delete(_id)
        return jsonify({'success': True}), 200
    return jsonify(client), 200


@blueprint.route('/clients/<_id>', methods=['DELETE'])
@admin_only
def delete(_id):
    """
    Deletes the client with given client id
    """
    get_resource_service('clients').delete_action(lookup={'_id': ObjectId(_id)})

    app.cache.delete(_id)
    return jsonify({'success': True}), 200
