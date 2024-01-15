import {createStore} from 'utils';

import {initViewData} from './actions';
import {companyAdminReducer} from './reducers';
import {CompanyAdminApp} from './components/CompanyAdminApp';
import {render} from 'render-utls';

const store = createStore(companyAdminReducer, 'CompanyAdmin');

if (window.viewData) {
    store.dispatch(initViewData(window.viewData));
}

render(store, CompanyAdminApp, document.getElementById('company-admin-app'));
