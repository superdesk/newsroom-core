import {
    UPDATE_NOTIFICATION_COUNT,
    SET_NOTIFICATIONS,
    SET_NOTIFICATIONS_LOADING,
    INIT_DATA,
    CLEAR_NOTIFICATION,
    CLEAR_ALL_NOTIFICATIONS,
} from './actions';

const initialState = {
    user: null,
    items: {},
    notifications: [],
    notificationCount: 0,
    loading: false,
};

export default function notificationReducer(state = initialState, action: any): any {
    switch (action.type) {
    case SET_NOTIFICATIONS:
        return {
            ...state,
            notifications: action.notifications,
            notificationCount: action.notifications.length,
            items: action.items.reduce((itemMap: any, item: any) => {
                itemMap[item._id] = item;

                return itemMap;
            }, {}),
        };

    case SET_NOTIFICATIONS_LOADING:
        return {
            ...state,
            loading: action.loading,
        };

    case UPDATE_NOTIFICATION_COUNT: {
        return {
            ...state,
            notificationCount: state.notificationCount + action.count,
        };
    }

    case CLEAR_ALL_NOTIFICATIONS:
        return {
            ...state,
            notifications: [],
            notificationCount: 0,
        };


    case CLEAR_NOTIFICATION:{
        const notifications = state.notifications.filter((n: any) => n.item !== action.id);
        return {
            ...state,
            notifications: notifications,
            notificationCount: notifications.length,
        };
    }

    case INIT_DATA: {
        return {
            ...state,
            user: action.data.user || null,
            items: {},
            notifications: [],
            notificationCount: action.data.notificationCount,
            loading: false,
        };
    }

    default:
        return state;
    }
}
