import {createStore, getInitData} from 'utils';
import {initWebSocket} from 'websocket';
import homeReducer from './reducers';
import HomeApp from './components/HomeApp';
import {initData, pushNotification} from './actions';
import {render} from 'render-utls';


const store = createStore(homeReducer, 'Home');


if (window.homeData) {
    const data = getInitData({...window.homeData, currentUser: {...window.profileData.user}});

    store.dispatch(initData(data));
}

render(
    store,
    HomeApp,
    document.getElementById('home-app')
);

initWebSocket(store, pushNotification);
