import React from 'react';

import {formatDate, gettext} from 'utils';
import {IArticle, IUser} from 'interfaces';

import NotificationListItem from './NotificationListItem';
import {INotification} from 'interfaces/notification';

export interface IProps {
    items: {[key: string]: IArticle};
    count: number;
    fullUser: IUser;
    notifications: Array<INotification>;
    loading: boolean;
    clearNotification(id: IUser['_id']): void;
    clearAll(): void;
    loadNotifications(): void;
    resumeNotifications(): void;
}

export const NotificationPopup = (props: IProps) => {
    const now = new Date();
    const pausedFrom = props.fullUser.notification_schedule?.pause_from ?? '';
    const pausedTo = props.fullUser.notification_schedule?.pause_to ?? '';
    const notificationsArePaused = (
        pausedFrom != '' && new Date(pausedFrom) < now &&
        pausedTo != '' && new Date(pausedTo) > now
    );

    if (notificationsArePaused) {
        return (
            <div className="notif__list dropdown-menu dropdown-menu-right show">
                <div className='notif__list__header d-flex'>
                    <span className='notif__list__header-headline ms-3'>{gettext('Notifications')}</span>
                </div>

                <div className='d-flex flex-column gap-2 p-3'>
                    <div className='nh-container nh-container__text--alert p-2'>
                        {gettext('All notifications are paused until {{date}}', {date: formatDate(pausedTo)})}
                    </div>

                    <button
                        type="button"
                        className="nh-button nh-button--small nh-button--tertiary"
                        onClick={() => {
                            props.resumeNotifications();
                        }}
                    >
                        {gettext('Resume all notifications')}
                    </button>
                </div>
            </div>
        );
    } else {
        if (props.count === 0) {
            return (
                <div className="notif__list dropdown-menu dropdown-menu-right show">
                    <div className='notif__list__header d-flex'>
                        <span className='notif__list__header-headline ms-3'>{gettext('Notifications')}</span>
                    </div>

                    <div className='notif__list__message'>
                        {gettext('No new notifications!')}
                    </div>
                </div>
            );
        } else {
            return (
                <div className="notif__list dropdown-menu dropdown-menu-right show">
                    <div className='notif__list__header d-flex'>
                        <span className='notif__list__header-headline ms-3'>{gettext('Notifications')}</span>
                        <button
                            type="button"
                            className="button-pill ms-auto me-3"
                            onClick={props.clearAll}
                        >
                            {gettext('Clear All')}
                        </button>
                    </div>

                    {(pausedFrom != '' && pausedTo != '' && notificationsArePaused === false) && (
                        <div className='p-3'>
                            <div className='nh-container nh-container__text--info p-2'>
                                {gettext('All notifications are set to be paused from {{dateFrom}} to {{dateTo}}', {dateFrom: formatDate(pausedFrom), dateTo: formatDate(pausedTo)})}
                            </div>
                        </div>
                    )}

                    {props.loading ? (
                        <div className='notif__list__message'>
                            {gettext('Loading...')}
                        </div>
                    ) : (
                        props.notifications.map((notification, index) => (
                            <NotificationListItem
                                key={notification._id || index}
                                item={notification.item in props.items ? props.items[notification.item] : notification.data?.item}
                                notification={notification}
                                clearNotification={props.clearNotification}
                            />
                        ))
                    )}
                </div>
            );
        }
    }
};
