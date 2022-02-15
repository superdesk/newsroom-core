import * as React from 'react';
import {get} from 'lodash';

import {gettext, shortDate} from 'utils';
import {BasicNotificationItem} from './BasicNotificationItem';

export const registeredNotifications = [];

export function registerNotification(condition, component) {
    registeredNotifications.unshift({condition, component});
}

export function renderNotificationComponent(notification, item) {
    let notificationEntry = registeredNotifications.find(
        (entry) => entry.condition(notification, item)
    );

    if (notificationEntry == null || notificationEntry.component == null) {
        console.error('Unable to find Notification Item component', notification, item);

        return null;
    }

    return notificationEntry.component(notification, item);
}

function getNotificationFooterText(notification) {
    switch (notification.action) {
    case 'share':
        return gettext('Shared by {{ first_name }} {{ last_name }} on {{ datetime }}', {
            first_name: get(notification, 'data.shared_by.first_name'),
            last_name: get(notification, 'data.shared_by.last_name'),
            datetime: shortDate(notification.created),
        });
    case 'topic_matches':
        return gettext('Created on {{ datetime }}', {datetime: shortDate(notification.created)});
    case 'history_match':
    default:
        return gettext('Updated on {{ datetime }}', {datetime: shortDate(notification.created)});
    }
}

function getNotificationUrl(notification, item) {
    if (get(notification, 'data.url')) {
        return notification.data.url;
    }

    return notification.resource === 'agenda' ?
        `/wire?item=${item._id}` :
        `/agenda?item=${item._id}`;
}

function getNotificationName(item) {
    return item.label || item.name || item.headline || item.slugline;
}

// New Wire item that matches action history (such as item Downloaded)
registerNotification(
    (notification, item) => (
        (get(notification, 'action') === 'history_match' && get(notification, 'resource') === 'text') ||
        // Fallback Wire notification (legacy functionality)
        get(notification, 'resource') === 'text' || item.type === 'text'
    ),
    (notification, item) => (
        <BasicNotificationItem
            header={gettext('A story you downloaded has been updated')}
            body={getNotificationName(item)}
            url={getNotificationUrl(notification, item)}
            footer={getNotificationFooterText(notification)}
        />
    )
);

// New Agenda item that matches action history (such as item Downloaded)
registerNotification(
    (notification, item) => (
        (get(notification, 'action') === 'history_match' && get(notification, 'resource') === 'agenda') ||
        (get(notification, 'action') === 'watched_agenda_updated') ||
        // Fallback Agenda notification (legacy functionality)
        get(notification, 'resource') === 'agenda' || item.type === 'agenda'
    ),
    (notification, item) => (
        <BasicNotificationItem
            header={gettext('An event you are watching has been updated')}
            body={getNotificationName(item)}
            url={getNotificationUrl(notification, item)}
            footer={getNotificationFooterText(notification)}
        />
    )
);

// New Wire/Agenda item matches a subscribed topic
registerNotification(
    (notification) => (
        get(notification, 'action') === 'topic_matches' &&
        ['text', 'wire', 'items', 'agenda'].includes(get(notification, 'resource'))
    ),
    (notification, item) => (
        <BasicNotificationItem
            header={notification.resource === 'agenda' ?
                gettext('An Agenda item has arrived that matches a subscribed topic') :
                gettext('A story has arrived that matches a subscribed topic')
            }
            body={getNotificationName(item)}
            url={getNotificationUrl(notification, item)}
            footer={getNotificationFooterText(notification)}
        />
    )
);

// A Topic was shared with this User
registerNotification(
    (notification) => (
        notification &&
        notification.action === 'share' &&
        notification.resource === 'topic'
    ),
    (notification, item) => (
        <BasicNotificationItem
            header={item.topic_type === 'agenda' ?
                gettext('An Agenda Topic has been shared with you') :
                gettext('A Wire Topic has been shared with you')
            }
            body={getNotificationName(item)}
            url={getNotificationUrl(notification, item)}
            footer={getNotificationFooterText(notification)}
        />
    )
);

// A Wire/Agenda item was shared with this user
registerNotification(
    (notification) => (
        get(notification, 'action') === 'share' &&
        ['text', 'wire', 'items', 'agenda'].includes(get(notification, 'resource'))
    ),
    (notification, item) => (
        <BasicNotificationItem
            header={notification.resource === 'agenda' ?
                gettext('An Agenda item was shared with you') :
                gettext('A Wire item was shared with you')
            }
            body={getNotificationName(item)}
            url={getNotificationUrl(notification, item)}
            footer={getNotificationFooterText(notification)}
        />
    )
);
