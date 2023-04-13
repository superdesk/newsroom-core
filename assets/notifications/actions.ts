import {get} from 'lodash';
import {gettext, notify, errorHandler} from 'utils';
import server from 'server';

export const UPDATE_NOTIFICATION_COUNT = 'UPDATE_NOTIFICATION_COUNT';
export function updateNotificationCount(count: any): any {
    return {type: UPDATE_NOTIFICATION_COUNT, count};
}

export const INIT_DATA = 'INIT_DATA';
export function initData(data: any): any {
    return {type: INIT_DATA, data};
}


export const CLEAR_ALL_NOTIFICATIONS = 'CLEAR_ALL_NOTIFICATIONS';
export function clearAllNotifications(): any {
    return {type: CLEAR_ALL_NOTIFICATIONS};
}


export const CLEAR_NOTIFICATION = 'CLEAR_NOTIFICATION';
export function clearNotification(id: any): any {
    return {type: CLEAR_NOTIFICATION, id};
}

export const SET_NOTIFICATIONS = 'SET_NOTIFICATIONS';
export function setNotifications(items: any, notifications: any): any {
    return {
        type: SET_NOTIFICATIONS,
        items: items,
        notifications: notifications,
    };
}

export const SET_NOTIFICATIONS_LOADING = 'SET_NOTIFICATIONS_LOADING';
export function setNotificationsLoading(loading: any): any {
    return {type: SET_NOTIFICATIONS_LOADING, loading};
}

export function loadNotifications(): any {
    return function (dispatch: any, getState: any) {
        dispatch(setNotificationsLoading(true));
        const user = getState().user;

        return server.get(`/users/${user}/notifications`)
            .then((data: any) => {
                dispatch(setNotifications(data.items, data.notifications));
            })
            .catch((error: any) => errorHandler(error, dispatch))
            .finally(() => {
                dispatch(setNotificationsLoading(false));
            });
    };
}


/**
 * Deletes the given notification of the user
 *
 */
export function deleteNotification(id: any): any {
    return function (dispatch: any, getState: any) {
        const user = getState().user;
        const url = `/users/${user}/notifications/${user}_${id}`;
        return server.del(url)
            .then(() => {
                notify.success(gettext('Notification cleared successfully'));
                dispatch(clearNotification(id));
            })
            .catch((error: any) => errorHandler(error, dispatch));
    };
}


/**
 * Deletes all notifications for the user
 *
 */
export function deleteAllNotifications(): any {
    return function (dispatch: any, getState: any) {
        const user = getState().user;
        const url = `/users/${user}/notifications`;
        return server.del(url)
            .then(() => {
                notify.success(gettext('Notifications cleared successfully'));
                dispatch(clearAllNotifications());
            })
            .catch((error: any) => errorHandler(error, dispatch));
    };
}


/**
 * Handle server push notification
 *
 * @param {Object} push
 */
export function pushNotification(push: any): any {
    return (dispatch: any, getState: any) => {
        const user = getState().user;
        switch (push.event) {
        case 'new_notifications':
            if (get(push, `extra.counts[${user}]`) != null) {
                dispatch(updateNotificationCount(push.extra.counts[user]));
            }
            break;
        }
    };
}
