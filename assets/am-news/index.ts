import {get, startsWith} from 'lodash';

import {createStore, getInitData, closeItemOnMobile, isMobilePhone} from '../utils';
import {initWebSocket} from 'websocket';

import {getReadItems} from 'local-store';
import  AmNewsApp from './components/AmNewsApp';
import wireReducer from '../wire/reducers';
import {
    fetchItems,
    initData,
    initParams,
    pushNotification,
    setState,
    openItemDetails,
    previewItem,
} from '../wire/actions';
import {
    toggleNavigation,
    toggleNavigationById,
} from '../search/actions';
import {render} from 'render-utls';

const store = createStore(wireReducer, 'AM');

// init data
store.dispatch(initData(getInitData(window.amNewsData), getReadItems(), false));

// init query
const params = new URLSearchParams(window.location.search);
store.dispatch(initParams(params));


// init first navigations - only if not loading a page to preview an item
const firstNavigation = startsWith(window.location.search, '?item=') ? null :
    get(window.amNewsData, 'navigations[0]');
const navigationId = params.get('navigation');
if (navigationId) {
    store.dispatch(toggleNavigationById(navigationId));
} else if (firstNavigation && !get(window.amNewsData, 'bookmarks', false)) {
    store.dispatch(toggleNavigation(firstNavigation));
}

// handle history
window.onpopstate = function(event: any) {
    if (event.state) {
        closeItemOnMobile(store.dispatch, event.state, openItemDetails, previewItem);
        if (!isMobilePhone()) {
            store.dispatch(setState(event.state));
        }
    }
};

// fetch items & render if there are navigations
store.dispatch(fetchItems()).then(() =>
    render(store, AmNewsApp, document.getElementById('am-news-app'))
);

// initialize web socket listener
initWebSocket(store, pushNotification);
