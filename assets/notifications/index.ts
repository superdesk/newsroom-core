import {createStore, render, initWebSocket} from 'assets/utils';
import notificationReducer from './reducers';
import NotificationApp from './components/NotificationsApp';
import {initData, pushNotification} from './actions';


const store = createStore(notificationReducer, 'Notifications');


if (window.notificationData) {
    store.dispatch(initData(window.notificationData));
}


render(store, NotificationApp, document.getElementById('header-notification'));


initWebSocket(store, pushNotification);

