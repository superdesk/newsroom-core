import React from 'react';
import PropTypes from 'prop-types';

import CloseButton from './CloseButton';
import {renderNotificationComponent} from 'notifications/components/notificationItems';

function NotificationListItem({notification, item, clearNotification}: any) {
    return (
        <div key={item._id} className='notif__list__item'>
            <CloseButton onClick={() => clearNotification(item._id)}/>
            {renderNotificationComponent(notification, item)}
        </div>);

}

NotificationListItem.propTypes = {
    notification: PropTypes.object,
    item: PropTypes.object,
    clearNotification: PropTypes.func,
};

export default NotificationListItem;
