import {isWireContext} from 'utils';
import {initWebSocket} from 'websocket';
import UserProfileApp from './components/UserProfileApp';
import {initData, selectMenu, pushNotification} from './actions';
import {store} from './store';
import {render} from 'render-utils';
import {WIRE_TOPIC_FOLDERS_UPDATED} from './constants';

if (window.profileData) {
    store.dispatch(initData(window.profileData));
}

let previousState = store.getState();

store.subscribe(() => {
    const currentState = store.getState();

    if (
        currentState.userFolders != previousState.userFolders
        || currentState.companyFolders != previousState.companyFolders
    ) {
        document.dispatchEvent(new CustomEvent(
            WIRE_TOPIC_FOLDERS_UPDATED,
            {detail: {companyId: currentState.company, userId: currentState.user._id}})
        );
    }

    previousState = currentState;
});

render(
    store,
    UserProfileApp,
    document.getElementById('header-profile-toggle')
);

document.addEventListener('manage_topics', function () {
    isWireContext() ? store.dispatch(selectMenu('topics')) : store.dispatch(selectMenu('events'));
}, false);

initWebSocket(store, pushNotification);
