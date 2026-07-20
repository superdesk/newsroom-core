import React from 'react';
import PropTypes from 'prop-types';

import CloseModalButton from './CloseModalButton';
import {renderNotificationComponent} from 'notifications/components/notificationItems';

function NotificationListItem({notification, item, clearNotification}: any) {
    if (item == null) {
        // rendering without an item throws and takes the whole notification list down
        console.warn('Skipping notification without an item', notification);

        return null;
    }

    return (
        <div className='notif__list__item'>
            <CloseModalButton onClick={() => clearNotification(notification.item)}/>
            {renderNotificationComponent(notification, item)}
        </div>);

}

NotificationListItem.propTypes = {
    notification: PropTypes.object,
    item: PropTypes.object,
    clearNotification: PropTypes.func,
};

export default NotificationListItem;
