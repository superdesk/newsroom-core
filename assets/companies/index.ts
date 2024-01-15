import {createStore} from 'utils';
import companyReducer from './reducers';
import CompaniesApp from './components/CompaniesApp';
import {initViewData, onURLParamsChanged} from './actions';
import {render} from 'render-utls';

const store = createStore(companyReducer, 'Company');

if (window.viewData) {
    store.dispatch(initViewData(window.viewData));
}

// Respond to URL param changes from browser history events
window.addEventListener('popstate', () => {
    store.dispatch(onURLParamsChanged());
});
store.dispatch(onURLParamsChanged());

render(store, CompaniesApp, document.getElementById('settings-app'));
