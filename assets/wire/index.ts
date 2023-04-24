import {getNewsOnlyParam, getReadItems, getSearchAllVersionsParam} from 'assets/local-store';
import {setView} from 'assets/search/actions';
import {closeItemOnMobile, createStore, getInitData, initWebSocket, isMobilePhone, render} from 'assets/utils';
import {
    fetchItems,
    initData,
    initParams,
    openItemDetails,
    previewItem,
    pushNotification,
    setState,
} from './actions';
import WireApp from './components/WireApp';
import wireReducer from './reducers';

const store = createStore(wireReducer, 'Wire');

// init data
store.dispatch(
    initData(
        getInitData(window.wireData),
        window.newsroom.client_config.news_only_filter,
        getReadItems(),
        getNewsOnlyParam(),
        getSearchAllVersionsParam())
);

// init view
if (localStorage.getItem('view')) {
    store.dispatch(setView(localStorage.getItem('view')));
}

// handle history
window.onpopstate = function(event) {
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
