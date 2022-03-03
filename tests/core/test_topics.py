from flask import json
from unittest import mock

from newsroom.topics.views import get_topic_url
from ..fixtures import PUBLIC_USER_NAME, init_company, PUBLIC_USER_ID, TEST_USER_ID  # noqa
from ..utils import mock_send_email

topic = {
    'label': 'Foo',
    'query': 'foo',
    'notifications': False,
    'topic_type': 'wire',
    'navigation': ['xyz'],
}

agenda_topic = {
    'label': 'Foo',
    'query': 'foo',
    'notifications': False,
    'topic_type': 'agenda',
    'navigation': ['abc'],
}

user_id = str(PUBLIC_USER_ID)
test_user_id = str(TEST_USER_ID)
topics_url = 'users/%s/topics' % user_id


def test_topics_no_session(client, anonymous_user):
    resp = client.get(topics_url)
    assert 302 == resp.status_code
    resp = client.post(topics_url, data=topic)
    assert 302 == resp.status_code


def test_post_topic_user(client):
    with client as cli:
        with client.session_transaction() as session:
            session['user'] = user_id
            session['name'] = PUBLIC_USER_NAME
        resp = cli.post(topics_url, json=topic)
        assert 201 == resp.status_code
        resp = cli.get(topics_url)
        assert 200 == resp.status_code
        data = json.loads(resp.get_data())
        assert 1 == len(data['_items'])


def test_update_topic_fails_for_different_user(client):
    with client as app:
        with client.session_transaction() as session:
            session['user'] = user_id
            session['name'] = PUBLIC_USER_NAME
        resp = app.post(topics_url, json=topic)
        assert 201 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        _id = data['_items'][0]['_id']

        with client.session_transaction() as session:
            session['name'] = test_user_id
            session['user'] = test_user_id
        resp = app.post('topics/{}'.format(_id), json={'label': 'test123'})
        assert 403 == resp.status_code


def test_update_topic(client):
    with client as app:
        with client.session_transaction() as session:
            session['user'] = user_id
            session['name'] = PUBLIC_USER_NAME
        resp = app.post(topics_url, json=topic)
        assert 201 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        _id = data['_items'][0]['_id']

        resp = app.post('topics/{}'.format(_id), data=json.dumps({'label': 'test123'}), content_type='application/json')
        assert 200 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        assert 'test123' == data['_items'][0]['label']


def test_delete_topic(client):
    with client as app:
        with client.session_transaction() as session:
            session['user'] = user_id
            session['name'] = PUBLIC_USER_NAME
        resp = app.post(topics_url, json=topic, content_type='application/json')
        assert 201 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        _id = data['_items'][0]['_id']

        resp = app.delete('topics/{}'.format(_id))
        assert 200 == resp.status_code

        resp = app.get(topics_url)
        data = json.loads(resp.get_data())
        assert 0 == len(data['_items'])


@mock.patch('newsroom.email.send_email', mock_send_email)
def test_share_wire_topics(client, app):
    topic_ids = app.data.insert('topics', [topic])
    topic['_id'] = topic_ids[0]

    with app.mail.record_messages() as outbox:
        with client.session_transaction() as session:
            session['user'] = user_id
            session['name'] = 'tester'
        resp = client.post('/topic_share', json={
            'items': topic,
            'users': [test_user_id],
            'message': 'Some info message',
        })

        assert resp.status_code == 201, resp.get_data().decode('utf-8')
        assert len(outbox) == 1
        assert outbox[0].recipients == ['test@bar.com']
        assert outbox[0].sender == 'newsroom@localhost'
        assert outbox[0].subject == 'From AAP Newsroom: %s' % topic['label']
        assert 'Hi Test Bar' in outbox[0].body
        assert 'Foo Bar (foo@bar.com) shared ' in outbox[0].body
        assert topic['query'] in outbox[0].body
        assert 'Some info message' in outbox[0].body
        assert '/wire' in outbox[0].body


@mock.patch('newsroom.email.send_email', mock_send_email)
def test_share_agenda_topics(client, app):
    topic_ids = app.data.insert('topics', [agenda_topic])
    agenda_topic['_id'] = topic_ids[0]

    with app.mail.record_messages() as outbox:
        with client.session_transaction() as session:
            session['user'] = user_id
            session['name'] = 'tester'
        resp = client.post('/topic_share', json={
            'items': agenda_topic,
            'users': [test_user_id],
            'message': 'Some info message',
        })

        assert resp.status_code == 201, resp.get_data().decode('utf-8')
        assert len(outbox) == 1
        assert outbox[0].recipients == ['test@bar.com']
        assert outbox[0].sender == 'newsroom@localhost'
        assert outbox[0].subject == 'From AAP Newsroom: %s' % agenda_topic['label']
        assert 'Hi Test Bar' in outbox[0].body
        assert 'Foo Bar (foo@bar.com) shared ' in outbox[0].body
        assert agenda_topic['query'] in outbox[0].body
        assert 'Some info message' in outbox[0].body
        assert '/agenda' in outbox[0].body


def test_get_topic_share_url(app):
    topic = {'topic_type': 'wire', 'query': 'art exhibition'}
    assert get_topic_url(topic) == 'http://localhost:5050/wire?q=art+exhibition'

    topic = {'topic_type': 'wire', 'filter': {"location": [["Sydney"]]}}
    assert get_topic_url(topic) == 'http://localhost:5050/wire?filter=%7B%22location%22%3A+%5B%5B%22Sydney%22%5D%5D%7D'

    topic = {'topic_type': 'wire', 'navigation': ['123']}
    assert get_topic_url(topic) == 'http://localhost:5050/wire?navigation=%5B%22123%22%5D'

    topic = {'topic_type': 'wire', 'navigation': ['123', '456']}
    assert get_topic_url(topic) == 'http://localhost:5050/wire?navigation=%5B%22123%22%2C+%22456%22%5D'

    topic = {'topic_type': 'wire', 'created': {'from': '2018-06-01'}}
    assert get_topic_url(topic) == 'http://localhost:5050/wire?created=%7B%22from%22%3A+%222018-06-01%22%7D'

    topic = {
        'topic_type': 'wire',
        'query': 'art exhibition',
        'filter': {"urgency": [3]},
        'navigation': ['123'],
        'created': {'from': '2018-06-01'},
    }
    assert get_topic_url(topic) == 'http://localhost:5050/wire?' \
                                   'q=art+exhibition' \
                                   '&filter=%7B%22urgency%22%3A+%5B3%5D%7D' \
                                   '&navigation=%5B%22123%22%5D' \
                                   '&created=%7B%22from%22%3A+%222018-06-01%22%7D'
