import {createStore} from 'utils';
import settingsReducer from './reducers';
import GeneralSettingsApp from './components/GeneralSettingsApp';
import {initViewData} from './actions';
import {render} from 'render-utls';


const store = createStore(settingsReducer, 'GeneralSettings');


if (window.viewData) {
    store.dispatch(initViewData(window.viewData));
}


render(store, GeneralSettingsApp, document.getElementById('settings-app'));
