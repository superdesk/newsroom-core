import {createStore, render, getInitData, closeItemOnMobile, isMobilePhone} from 'utils';
import {initWebSocket} from 'websocket';

import wireReducer from './reducers';
import {getNewsOnlyParam, getSearchAllVersionsParam, getReadItems} from 'local-store';
import WireApp from './components/WireApp';
import {
    fetchItems,
    setState,
    initData,
    pushNotification,
    initParams,
    openItemDetails,
    previewItem,
    fetchFoldersWire,
} from './actions';
import {setView} from 'search/actions';
import {WIRE_TOPIC_FOLDERS_UPDATED} from 'user-profile';

const store = createStore(wireReducer, 'Wire');

// init data
store.dispatch(initData(getInitData(window.wireData), window.newsroom.client_config.news_only_filter, getReadItems(), getNewsOnlyParam(), getSearchAllVersionsParam()));

// init view
if (localStorage.getItem('view')) {
    store.dispatch(setView(localStorage.getItem('view')));
}

// handle history
window.onpopstate = function(event: any) {
    if (event.state) {
        closeItemOnMobile(store.dispatch, event.state, openItemDetails, previewItem);
        if (!isMobilePhone()) {
            store.dispatch(setState(event.state));
            store.dispatch(fetchItems());
        }
    }
};

// init query, filter, navigation and start date
const params = new URLSearchParams(window.location.search);
store.dispatch(initParams(params));

// start fetching items, must be before rendering WireApp to show loader
store.dispatch(fetchItems());

// render app
render(store, WireApp, document.getElementById('wire-app'));

// initialize web socket listener
initWebSocket(store, pushNotification);

document.addEventListener(WIRE_TOPIC_FOLDERS_UPDATED, (_e) => {
    const e: CustomEvent = _e as CustomEvent;
    const {companyId, userId} = e.detail;

    store.dispatch(fetchFoldersWire(companyId, userId));
});
