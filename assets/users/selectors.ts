import {get} from 'lodash';

export const userSelector = (state: any) => get(state, 'user');
