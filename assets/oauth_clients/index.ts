import {createStore} from 'utils';
import {render} from 'render-utls';
import clientReducer from './reducers';
import ClientsApp from './components/ClientsApp';
import {initViewData} from './actions';

const store = createStore(clientReducer, 'oauth_clients');


if (window.viewData && window.viewData.oauth_clients) {
    store.dispatch(initViewData(window.viewData));
}


render(store, ClientsApp, document.getElementById('settings-app'));
