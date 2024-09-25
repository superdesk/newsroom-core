import {createStore} from 'utils';
import {render} from 'render-utils';
import sectionFiltersReducer from './reducers';
import SectionFiltersApp from './components/SectionFiltersApp';
import {initViewData} from './actions';
import 'user-profile';


const store = createStore(sectionFiltersReducer, 'SectionFilters');


if (window.viewData) {
    store.dispatch(initViewData(window.viewData));
}


render(store, SectionFiltersApp, document.getElementById('settings-app'));
