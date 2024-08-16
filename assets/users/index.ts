import {createStore} from 'utils';
import {render} from 'render-utils';
import userReducer from './reducers';
import UsersApp from './components/UsersApp';
import {initViewData, onURLParamsChanged} from './actions';
import 'user-profile';

const store = createStore(userReducer, 'Users');

if (window.viewData) {
    store.dispatch(initViewData(window.viewData));
}

// Respond to URL param changes from browser history events
window.addEventListener('popstate', () => {
    store.dispatch(onURLParamsChanged());
});
store.dispatch(onURLParamsChanged());

render(store, UsersApp, document.getElementById('settings-app'));
