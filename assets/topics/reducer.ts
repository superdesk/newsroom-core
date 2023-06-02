
import {
    SET_TOPICS
} from './actions';

const initialState: Array<any> = [];

export function topicsReducer(state = initialState, action: any) {
    switch (action.type) {
    case SET_TOPICS:
        return action.topics;

    default:
        return state;
    }
}