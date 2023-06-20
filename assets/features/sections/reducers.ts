import {
    INIT_SECTIONS,
    SELECT_SECTION,
} from './actions';

const INITIAL_STATE = {
    list: [],
    active: '',
};

export function sectionsReducer(state: any = INITIAL_STATE, action?: any): any {
    if (!action) {
        return state;
    }

    switch (action.type) {

    case INIT_SECTIONS:
        return {...state, list: action.sections, active: action.sections[0]._id};

    case SELECT_SECTION:
        return {...state, active: action.section || ''};

    default:
        return state;
    }
}