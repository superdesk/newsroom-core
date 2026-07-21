import React from 'react';

import {IArticle} from 'interfaces';
import {INotification} from 'interfaces/notification';

import CloseModalButton from './CloseModalButton';
import {renderNotificationComponent} from 'notifications/components/notificationItems';

interface IProps {
    notification: INotification;
    item: IArticle;
    clearNotification(id: string): void;
}

function NotificationListItem({notification, item, clearNotification}: IProps) {
    return (
        <div className='notif__list__item'>
            <CloseModalButton onClick={() => clearNotification(notification.item)}/>
            {renderNotificationComponent(notification, item)}
        </div>
    );
}

export default NotificationListItem;
