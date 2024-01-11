import {IPublicAppState} from 'interfaces';
import {createStore, render} from 'utils';
import {PublicApp} from './components/PublicApp';
import {publicAppReducer} from './reducers';
import {initData} from 'actions';

const store = createStore<IPublicAppState>(publicAppReducer, 'Public');

if (window.viewData) {
    store.dispatch(initData(window.viewData));
}

render(
    store,
    PublicApp,
    document.getElementById('public-app')
);
