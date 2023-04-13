import {createStore} from 'assets/utils';
import userReducer from './reducers';


export const store = createStore(userReducer, 'UserProfile');
