import re

import flask
from bson import ObjectId
from flask import jsonify, current_app as app
from flask_babel import gettext
from superdesk import get_resource_service
from werkzeug.exceptions import NotFound

from newsroom.decorator import admin_only, account_manager_only
from newsroom.clients import blueprint
from newsroom.utils import query_resource, find_one, get_json_or_400


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

    new_company = get_client_updates(client)
    ids = get_resource_service('clients').post([new_company])
    return jsonify({'success': True, '_id': ids[0]}), 201


@blueprint.route('/clients/<_id>', methods=['GET', 'POST'])
@account_manager_only
def edit(_id):
    """
    Edits the client with given client id
    """
    company = find_one('clients', _id=ObjectId(_id))

    if not company:
        return NotFound(gettext('Client not found'))

    if flask.request.method == 'POST':
        company = get_json_or_400()

        updates = get_client_updates(company)
        get_resource_service('clients').patch(ObjectId(_id), updates=updates)
        app.cache.delete(_id)
        return jsonify({'success': True}), 200
    return jsonify(company), 200


@blueprint.route('/clients/<_id>', methods=['DELETE'])
@admin_only
def delete(_id):
    """
    Deletes the client with given client id
    """
    get_resource_service('clients').delete_action(lookup={'_id': ObjectId(_id)})

    app.cache.delete(_id)
    return jsonify({'success': True}), 200


def get_client_updates(client):
    updates = {
        'name': client.get('name'),
        'secret_key': ''
    }

    return updates
