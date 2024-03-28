import {IPublicAppState} from 'home/reducers';
import {createStore} from 'utils';
import {PublicApp} from './components/PublicApp';
import {publicAppReducer} from './reducers';
import {initData} from 'actions';
import {render} from 'render-utils';

const store = createStore<IPublicAppState>(publicAppReducer, 'Public');

if (window.viewData) {
    store.dispatch(initData(window.viewData));
}

render(
    store,
    PublicApp,
    document.getElementById('public-app')
);
