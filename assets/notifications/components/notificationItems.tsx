import * as React from 'react';
import {get} from 'lodash';

import {gettext, formatTime, formatDate, isToday} from 'utils';
import {BasicNotificationItem} from './BasicNotificationItem';

export const registeredNotifications = [];

export function registerNotification(condition: any, component: any) {
    registeredNotifications.unshift({condition, component});
}

export function renderNotificationComponent(notification: any, item: any) {
    let notificationEntry = registeredNotifications.find(
        (entry: any) => entry.condition(notification, item)
    );

    if (notificationEntry == null || notificationEntry.component == null) {
        console.error('Unable to find Notification Item component', notification, item);

        return null;
    }

    return notificationEntry.component(notification, item);
}

function getNotificationFooterText(notification: any) {
    switch (notification.action) {
    case 'share':
        return (
            isToday(notification.created) ?
                gettext('Shared by {{ first_name }} {{ last_name }} at {{ time }}', {
                    first_name: get(notification, 'data.shared_by.first_name'),
                    last_name: get(notification, 'data.shared_by.last_name'),
                    time: formatTime(notification.created),
                }) :
                gettext('Shared by {{ first_name }} {{ last_name }} on {{ date }}', {
                    first_name: get(notification, 'data.shared_by.first_name'),
                    last_name: get(notification, 'data.shared_by.last_name'),
                    date: formatDate(notification.created),
                })
        );
    case 'topic_matches':
        return (
            isToday(notification.created) ?
                gettext('Created at {{ time }}', {time: formatTime(notification.created)}) :
                gettext('Created on {{ date }}', {date: formatDate(notification.created)})
        );
    case 'history_match':
    default:
        return (
            isToday(notification.created) ?
                gettext('Updated at {{ time }}', {time: formatTime(notification.created)}) :
                gettext('Updated on {{ date }}', {date: formatDate(notification.created)})
        );
    }
}

function getNotificationUrl(notification: any, item: any) {
    if (get(notification, 'data.url')) {
        return notification.data.url;
    }

    return notification.resource === 'agenda' ?
        `/agenda?item=${item._id}` :
        `/wire?item=${item._id}`;
}

function getNotificationName(item: any) {
    return item.label || item.name || item.headline || item.slugline;
}

// New Wire item that matches action history (such as item Downloaded)
registerNotification(
    (notification: any, item: any) => (
        (get(notification, 'action') === 'history_match' && get(notification, 'resource') === 'text') ||
        // Fallback Wire notification (legacy functionality)
        get(notification, 'resource') === 'text' || item.type === 'text'
    ),
    (notification: any, item: any) => (
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
    (notification: any, item: any) => (
        (get(notification, 'action') === 'history_match' && get(notification, 'resource') === 'agenda') ||
        (get(notification, 'action') === 'watched_agenda_updated') ||
        // Fallback Agenda notification (legacy functionality)
        get(notification, 'resource') === 'agenda' || item.type === 'agenda'
    ),
    (notification: any, item: any) => (
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
    (notification: any) => (
        get(notification, 'action') === 'topic_matches' &&
        ['text', 'wire', 'items', 'agenda'].includes(get(notification, 'resource'))
    ),
    (notification: any, item: any) => (
        <BasicNotificationItem
            header={notification.resource === 'agenda' ?
                gettext('{{ agenda }} item has arrived that matches a subscribed topic', sectionNames) :
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
    (notification: any) => (
        notification &&
        notification.action === 'share' &&
        notification.resource === 'topic'
    ),
    (notification: any, item: any) => (
        <BasicNotificationItem
            header={gettext('{{ section }} Topic has been shared with you', {
                section: item.topic_type === 'agenda' ? sectionNames.agenda : sectionNames.wire,
            })}
            body={getNotificationName(item)}
            url={getNotificationUrl(notification, item)}
            footer={getNotificationFooterText(notification)}
        />
    )
);

// A Wire/Agenda item was shared with this user
registerNotification(
    (notification: any) => (
        get(notification, 'action') === 'share' &&
        ['text', 'wire', 'items', 'agenda'].includes(get(notification, 'resource'))
    ),
    (notification: any, item: any) => (
        <BasicNotificationItem
            header={gettext('{{ section }} item was shared with you', {
                section: notification.resource === 'agenda' ? sectionNames.agenda : sectionNames.wire,
            })}
            body={getNotificationName(item)}
            url={getNotificationUrl(notification, item)}
            footer={getNotificationFooterText(notification)}
        />
    )
);
