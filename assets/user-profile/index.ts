import {render, isWireContext} from 'utils';
import {initWebSocket} from 'websocket';
import UserProfileApp from './components/UserProfileApp';
import {initData, selectMenu, pushNotification} from './actions';
import {store} from './store';

if (window.profileData) {
    store.dispatch(initData(window.profileData));
}

/**
 * This constant needs to be defined here because of script loading.
 * If not it will break the tests because of the loading order.
 */
export const WIRE_TOPIC_FOLDERS_UPDATED = 'reload-wire-folders';

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
