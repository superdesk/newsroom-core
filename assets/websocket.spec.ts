import {initWebSocket} from 'websocket';
import {notify} from 'utils';

describe('websocket', () => {
    const originalWebSocket = window.WebSocket;
    const originalWebsocketUrl = window.newsroom.websocket;
    const originalProfileData = window.profileData;
    const createdSockets: Array<any> = [];

    class FakeWebSocket {
        static CLOSED = 3;

        readyState = 0;
        onerror: any;
        onopen: any;
        onclose: any;
        onmessage: any;
        url: string;
        close = jasmine.createSpy('close').and.callFake(() => {
            this.readyState = FakeWebSocket.CLOSED;
            if (this.onclose) {
                this.onclose({});
            }
        });

        constructor(url: string) {
            this.url = url;
            createdSockets.push(this);
        }
    }

    beforeEach(() => {
        createdSockets.length = 0;
        window.__newsroomWebSocketManager = undefined;
        window.WebSocket = FakeWebSocket as any;
        window.newsroom.websocket = 'ws://example.test';
        window.profileData = {
            user: {_id: 'user-1'},
            company: 'None',
        };
        spyOn(notify, 'success').and.stub();
        spyOn(notify, 'error').and.stub();
    });

    afterEach(() => {
        try {
            jasmine.clock().uninstall();
        } catch (e) {
            // clock may not have been installed
        }

        const manager = window.__newsroomWebSocketManager;

        if (manager && manager.unloadHandler) {
            window.removeEventListener('beforeunload', manager.unloadHandler);
        }

        if (manager && manager.connectInterval != null) {
            clearInterval(manager.connectInterval);
        }

        window.WebSocket = originalWebSocket;
        window.newsroom.websocket = originalWebsocketUrl;
        window.profileData = originalProfileData;
        window.__newsroomWebSocketManager = undefined;
    });

    it('shares a single websocket connection across multiple consumers', () => {
        const storeA = {dispatch: jasmine.createSpy('dispatchA')};
        const storeB = {dispatch: jasmine.createSpy('dispatchB')};

        initWebSocket(storeA, (data: any) => ({type: 'A', data}));
        initWebSocket(storeB, (data: any) => ({type: 'B', data}));

        expect(createdSockets.length).toBe(1);
        expect(window.__newsroomWebSocketManager?.listeners.length).toBe(2);
    });

    it('dispatches incoming messages to every consumer', () => {
        const storeA = {dispatch: jasmine.createSpy('dispatchA')};
        const storeB = {dispatch: jasmine.createSpy('dispatchB')};
        const actionA = jasmine.createSpy('actionA').and.callFake((data: any) => ({type: 'A', data}));
        const actionB = jasmine.createSpy('actionB').and.callFake((data: any) => ({type: 'B', data}));

        initWebSocket(storeA, actionA);
        initWebSocket(storeB, actionB);

        const socket = createdSockets[0] as any;
        const payload = {event: 'new_notifications', extra: {counts: {'user-1': 1}}};

        socket.onmessage({data: JSON.stringify(payload)});

        expect(storeA.dispatch).toHaveBeenCalledWith({type: 'A', data: payload});
        expect(storeB.dispatch).toHaveBeenCalledWith({type: 'B', data: payload});
    });

    it('dispatches websocket lifecycle events', () => {
        const store = {dispatch: jasmine.createSpy('dispatch')};
        const dispatchSpy = spyOn(window, 'dispatchEvent').and.callThrough();

        initWebSocket(store, (data: any) => ({type: 'A', data}));

        const socket = createdSockets[0] as any;

        socket.onopen();
        socket.close();

        expect(dispatchSpy.calls.all().some((call) => call.args[0].type === 'websocket:connected')).toBe(true);
        expect(dispatchSpy.calls.all().some((call) => call.args[0].type === 'websocket:disconnected')).toBe(true);
    });

    it('reconnects after a disconnect and shows the reconnect toast', () => {
        jasmine.clock().install();

        const store = {dispatch: jasmine.createSpy('dispatch')};
        const dispatchSpy = spyOn(window, 'dispatchEvent').and.callThrough();

        initWebSocket(store, (data: any) => ({type: 'A', data}));

        const socket1 = createdSockets[0] as any;

        socket1.onopen();
        expect(notify.success).not.toHaveBeenCalled();

        socket1.close();

        const manager = window.__newsroomWebSocketManager!;
        expect(manager.connectInterval).not.toBeNull();
        expect(dispatchSpy.calls.all().some((call) => call.args[0].type === 'websocket:disconnected')).toBe(true);

        jasmine.clock().tick(5000);

        expect(createdSockets.length).toBe(2);
        const socket2 = createdSockets[1] as any;

        socket2.onopen();

        expect(notify.success).toHaveBeenCalled();
        expect(dispatchSpy.calls.all().some((call) => call.args[0].type === 'websocket:connected')).toBe(true);
    });

    it('adds late subscribers without creating a new socket', () => {
        const storeA = {dispatch: jasmine.createSpy('dispatchA')};
        const storeB = {dispatch: jasmine.createSpy('dispatchB')};

        initWebSocket(storeA, (data: any) => ({type: 'A', data}));

        const socket = createdSockets[0] as any;
        socket.onopen();

        initWebSocket(storeB, (data: any) => ({type: 'B', data}));

        expect(createdSockets.length).toBe(1);

        const payload = {event: 'new_notifications', extra: {counts: {'user-1': 1}}};
        socket.onmessage({data: JSON.stringify(payload)});

        expect(storeA.dispatch).toHaveBeenCalledWith({type: 'A', data: payload});
        expect(storeB.dispatch).toHaveBeenCalledWith({type: 'B', data: payload});
    });

    it('closes the shared websocket during unload', () => {
        const store = {dispatch: jasmine.createSpy('dispatch')};

        initWebSocket(store, (data: any) => ({type: 'A', data}));

        const socket = createdSockets[0] as any;
        const manager = window.__newsroomWebSocketManager!;

        expect(socket.close).not.toHaveBeenCalled();

        manager.unloadHandler!();

        expect(socket.close).toHaveBeenCalled();
        expect(manager.shuttingDown).toBe(true);
    });

    it('does not create a new socket after unload', () => {
        const store = {dispatch: jasmine.createSpy('dispatch')};

        initWebSocket(store, (data: any) => ({type: 'A', data}));

        const manager = window.__newsroomWebSocketManager!;
        manager.unloadHandler!();

        initWebSocket({dispatch: jasmine.createSpy('dispatch2')}, (data: any) => ({type: 'B', data}));

        expect(createdSockets.length).toBe(1);
        expect(manager.shuttingDown).toBe(true);
    });
});
