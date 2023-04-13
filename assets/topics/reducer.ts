
import {
    SET_TOPICS
} from './actions';

const initialState = [];

export function topicsReducer(state=initialState, action: any): any {
    switch (action.type) {
    case SET_TOPICS:
        return action.topics;

    default:
        return state;
    }
}