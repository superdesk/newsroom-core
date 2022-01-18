from urllib import parse

from bson import ObjectId
from superdesk import get_resource_service
from flask import json, jsonify, abort, session, current_app as app
from flask_babel import gettext

from newsroom.topics import blueprint
from newsroom.topics.topics import get_user_topics as _get_user_topics
from newsroom.utils import find_one
from newsroom.auth import get_user, get_user_id
from newsroom.decorator import login_required
from newsroom.utils import get_json_or_400, get_entity_or_404
from newsroom.email import send_template_email
from newsroom.notifications import push_user_notification, push_company_notification


@blueprint.route('/users/<user_id>/topics', methods=['GET'])
@login_required
def get_user_topics(user_id):
    return jsonify(_get_user_topics(user_id)), 200


@blueprint.route('/topics/my_topics', methods=['GET'])
@login_required
def get_list_my_topics():
    return jsonify(_get_user_topics(get_user_id())), 200


@blueprint.route('/topics/<id>', methods=['POST'])
@login_required
def update_topic(id):
    """ Updates a followed topic """
    data = get_json_or_400()
    current_user = get_user(required=True)

    if not is_user_topic(id, str(current_user['_id'])):
        abort(403)

    # If notifications are enabled, check to see if user is configured to receive emails
    data.setdefault('subscribers', [])
    if str(current_user['_id']) in data['subscribers']:
        user = get_resource_service('users').find_one(req=None, _id=current_user['_id'])
        if not user.get('receive_email'):
            return "", gettext('Please enable \'Receive notifications via email\' option in your profile to receive topic notifications')  # noqa

    updates = {
        'label': data.get('label'),
        'query': data.get('query'),
        'created': data.get('created'),
        'filter': data.get('filter'),
        'navigation': data.get('navigation'),
        'company': current_user.get('company'),
        'subscribers': [
            ObjectId(uid)
            for uid in data['subscribers']
        ],
        'is_global': data.get('is_global', False),
    }

    original = get_resource_service('topics').find_one(req=None, _id=ObjectId(id))
    response = get_resource_service('topics').patch(id=ObjectId(id), updates=updates)
    if response.get('is_global') or updates.get('is_global', False) != original.get('is_global', False):
        push_company_notification('topics')
    else:
        push_user_notification('topics')
    return jsonify({'success': True}), 200


@blueprint.route('/topics/<id>', methods=['DELETE'])
@login_required
def delete(id):
    """ Deletes a followed topic by given id """
    if not is_user_topic(id, session['user']):
        abort(403)

    get_resource_service('topics').delete_action({'_id': ObjectId(id)})
    push_user_notification('topics')
    return jsonify({'success': True}), 200


def is_user_topic(topic_id, user_id):
    """
    Checks if the topic with topic_id belongs to user with user_id
    """
    topic = find_one('topics', _id=ObjectId(topic_id))
    user_ids = [user.get('id') for user in topic.get('users') or []]
    if topic and (str(topic.get('user')) == user_id or user_id in user_ids):
        return True
    return False


def get_topic_url(topic):
    query_strings = []
    if topic.get('query'):
        query_strings.append('q={}'.format(parse.quote(topic.get('query'))))
    if topic.get('filter'):
        query_strings.append('filter={}'.format(parse.quote(json.dumps(topic.get('filter')))))
    if topic.get('navigation'):
        query_strings.append(
            'navigation={}'.format(
                parse.quote(json.dumps(topic.get('navigation')))
            )
        )
    if topic.get('created'):
        query_strings.append('created={}'.format(parse.quote(json.dumps(topic.get('created')))))

    url = '{}/{}?{}'.format(
        app.config['CLIENT_URL'],
        topic.get('topic_type'),
        '&'.join(query_strings)
    )

    return url


@blueprint.route('/topic_share', methods=['POST'])
@login_required
def share():
    current_user = get_user(required=True)
    data = get_json_or_400()
    assert data.get('users')
    assert data.get('items')
    topic = get_entity_or_404(data.get('items')['_id'], 'topics')
    for user_id in data['users']:
        user = get_resource_service('users').find_one(req=None, _id=user_id)
        if not user or not user.get('email'):
            continue

        template_kwargs = {
            'recipient': user,
            'sender': current_user,
            'topic': topic,
            'url': get_topic_url(topic),
            'message': data.get('message'),
            'app_name': app.config['SITE_NAME'],
        }
        send_template_email(
            to=[user["email"]],
            template="share_topic",
            template_kwargs=template_kwargs,
        )
    return jsonify(), 201
