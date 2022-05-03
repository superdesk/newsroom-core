import {notify, gettext} from './utils';

const DEFAULT_WS_URL = 'ws://localhost:5150';
const RECONNECT_INTERVAL = 5000;

let firstConnection = true;
let wsConnection;
let connectInterval;
const listeners = [];

function connectToNotificationServer() {
    if (wsConnection == null || wsConnection.readyState === WebSocket.CLOSED) {
        wsConnection = new WebSocket(
            window.newsroom && window.newsroom.websocket ?
                window.newsroom.websocket :
                DEFAULT_WS_URL
        );
        wsConnection.onerror = onWebsocketError;
        wsConnection.onopen = onWebsocketOpen;
        wsConnection.onclose = onWebsocketClose;
        wsConnection.onmessage = onWebsocketMessage;
    }
}

export function initWebSocket(store, action) {
    connectToNotificationServer();
    listeners.push({store, action});
}

function onWebsocketError(event) {
    console.error(event);
}

function onWebsocketOpen() {
    if (!firstConnection) {
        // Only show notification if the connection was re-established
        // otherwise a notification will be shown when navigating to each page
        notify.success(gettext('Connected to Notification Server!'));
    }

    firstConnection = false;
    clearInterval(connectInterval);
    connectInterval = null;
    window.dispatchEvent(new Event('websocket:connected'));
}

function onWebsocketClose() {
    if (connectInterval != null) {
        // Already attempting to reconnect to the Notification Server
        // No need to add another interval
        return;
    }

    wsConnection = null;
    notify.error(gettext('Disconnected from Notification Server!'));
    window.dispatchEvent(new Event('websocket:disconnected'));

    connectInterval = setInterval(() => {
        connectToNotificationServer();
    }, RECONNECT_INTERVAL);
}

function onWebsocketMessage(message) {
    if (!message || !message.data) {
        console.error('Invalid websocket message', message);
        return;
    }

    const data = JSON.parse(message.data);

    if (!data || !data.event) {
        console.error('Invalid websocket message data', message.data);
        return;
    }

    listeners.forEach(({store, action}) => {
        store.dispatch(action(data));
    });
}
