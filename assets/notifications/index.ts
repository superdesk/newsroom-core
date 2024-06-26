import {createStore} from 'utils';
import {render} from 'render-utils';
import {initWebSocket} from 'websocket';
import notificationReducer from './reducers';
import NotificationApp from './components/NotificationsApp';
import {initData, pushNotification} from './actions';


const store = createStore(notificationReducer, 'Notifications');


if (window.notificationData) {
    store.dispatch(initData(window.notificationData, window.profileData));
}


render(store, NotificationApp, document.getElementById('header-notification'));


initWebSocket(store, pushNotification);

