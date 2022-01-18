import {createStore, render} from 'utils';
import clientReducer from './reducers';
import ClientsApp from './components/ClientsApp';
import {initViewData} from './actions';

const store = createStore(clientReducer, 'Client');


if (window.viewData && window.viewData.clients) {
    store.dispatch(initViewData(window.viewData));
}


render(store, ClientsApp, document.getElementById('settings-app'));
