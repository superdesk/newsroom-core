import {get} from 'lodash';
import {notify, gettext} from './utils';

const DEFAULT_WS_URL = 'ws://localhost:5150';
const RECONNECT_INTERVAL = 5000;

function getWebSocketManager(): INewsroomWebSocketManager {
    if (!window.__newsroomWebSocketManager) {
        window.__newsroomWebSocketManager = {
            firstConnection: true,
            wsConnection: null,
            connectInterval: null,
            listeners: [],
            shuttingDown: false,
            unloadHandlerAttached: false,
            unloadHandler: null,
        };
    }

    return window.__newsroomWebSocketManager;
}

function connectToNotificationServer() {
    const manager = getWebSocketManager();

    if (manager.shuttingDown) {
        return;
    }

    if (manager.wsConnection == null || manager.wsConnection.readyState === WebSocket.CLOSED) {
        const baseURL = window.newsroom && window.newsroom.websocket ?
            window.newsroom.websocket :
            DEFAULT_WS_URL;
        const wsURL = new URL(`${baseURL}/subscribe`);

        if (get(window, 'profileData.user._id')) {
            wsURL.searchParams.append('user', window.profileData.user._id);
        }
        if (get(window, 'profileData.company') && window.profileData.company !== 'None') {
            wsURL.searchParams.append('company', window.profileData.company);
        }

        manager.wsConnection = new WebSocket(wsURL.href);
        manager.wsConnection.onerror = onWebsocketError;
        manager.wsConnection.onopen = onWebsocketOpen;
        manager.wsConnection.onclose = onWebsocketClose;
        manager.wsConnection.onmessage = onWebsocketMessage;
    }
}

function shutdownNotificationServer() {
    const manager = getWebSocketManager();

    manager.shuttingDown = true;

    if (manager.connectInterval != null) {
        clearInterval(manager.connectInterval);
        manager.connectInterval = null;
    }

    if (manager.wsConnection != null) {
        manager.wsConnection.close();
        manager.wsConnection = null;
    }
}

function ensureUnloadHandler() {
    const manager = getWebSocketManager();

    if (manager.unloadHandlerAttached) {
        return;
    }

    manager.unloadHandlerAttached = true;
    manager.unloadHandler = shutdownNotificationServer;
    window.addEventListener('beforeunload', manager.unloadHandler);
}

export function initWebSocket(store: any, action: any) {
    const manager = getWebSocketManager();

    ensureUnloadHandler();
    manager.listeners.push({store, action});
    connectToNotificationServer();
}

function onWebsocketError(event: any) {
    console.error(event);
}

function onWebsocketOpen() {
    const manager = getWebSocketManager();

    if (!manager.firstConnection) {
        // Only show notification if the connection was re-established
        // otherwise a notification will be shown when navigating to each page
        notify.success(gettext('Connected to Notification Server!'));
    }

    manager.firstConnection = false;

    if (manager.connectInterval != null) {
        clearInterval(manager.connectInterval);
        manager.connectInterval = null;
    }

    window.dispatchEvent(new Event('websocket:connected'));
}

function onWebsocketClose() {
    const manager = getWebSocketManager();

    if (manager.shuttingDown) {
        if (manager.connectInterval != null) {
            clearInterval(manager.connectInterval);
            manager.connectInterval = null;
        }

        manager.wsConnection = null;
        return;
    }

    if (manager.connectInterval != null || manager.wsConnection == null) {
        // Already attempting to reconnect to the Notification Server
        // No need to add another interval
        return;
    }

    manager.wsConnection = null;
    notify.error(gettext('Disconnected from Notification Server!'));
    window.dispatchEvent(new Event('websocket:disconnected'));

    manager.connectInterval = setInterval(() => {
        connectToNotificationServer();
    }, RECONNECT_INTERVAL);
}

function onWebsocketMessage(message: any) {
    if (!message || !message.data) {
        console.error('Invalid websocket message', message);
        return;
    }

    const data = JSON.parse(message.data);

    if ((!data || !data.event) && !data.ping) {
        console.error('Invalid websocket message data', message.data);
        return;
    }

    const manager = getWebSocketManager();

    manager.listeners.forEach(({store, action}: IWebSocketListener) => {
        store.dispatch(action(data));
    });
}
