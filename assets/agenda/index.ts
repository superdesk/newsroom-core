import agendaReducer from './reducers';
import AgendaApp from './components/AgendaApp';
import {fetchItems, setState, initData, initParams, pushNotification, openItemDetails, previewItem} from './actions';
import {getReadItems, getActiveDate, getFeaturedOnlyParam} from 'assets/local-store';
import {setView} from 'assets/search/actions';
import {createStore, getInitData, closeItemOnMobile, isMobilePhone} from 'assets/utils';
import {initWebSocket} from 'assets/websocket';
import {render} from 'react-dom';

const store = createStore(agendaReducer, 'Agenda');

// init data
store.dispatch(initData(getInitData(window.agendaData), getReadItems(), getActiveDate(), getFeaturedOnlyParam()));


// init query
const params = new URLSearchParams(window.location.search);
store.dispatch(initParams(params));

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

// start fetching items before rendering
store.dispatch(fetchItems());

// render app
render(store as any, AgendaApp as any, document.getElementById('agenda-app') as any);

// initialize web socket listener
initWebSocket(store, pushNotification);
