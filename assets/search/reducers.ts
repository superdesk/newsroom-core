import {toggleValue} from 'utils';
import {get} from 'lodash';

import {
    SET_VIEW,
    TOGGLE_TOPIC,
    RESET_FILTER,
    TOGGLE_FILTER,
    TOGGLE_NAVIGATION,
    SET_CREATED_FILTER,

    SET_SEARCH_TOPIC_ID,
    SET_SEARCH_NAVIGATION_IDS,
    SET_SEARCH_QUERY,
    SET_SEARCH_FILTERS,
    SET_SEARCH_CREATED,
    SET_SEARCH_PRODUCT,
    RESET_SEARCH_PARAMS,
    TOGGLE_ADVANCED_SEARCH_FIELD,
    SET_ADVANCED_SEARCH_KEYWORDS,
    CLEAR_ADVANCED_SEARCH_PARAMS,
    SET_ADVANCED_SEARCH_PARAMS,
} from './actions';

import {EXTENDED_VIEW} from 'wire/defaults';

const ADVANCED_FIELDS = ['headline', 'slugline', 'body_html'];

const INITIAL_STATE = {
    activeTopic: null,
    activeNavigation: [],
    activeQuery: '',
    activeFilter: {},
    createdFilter: {},
    productId: null,

    navigations: [],
    products: [],

    activeView: EXTENDED_VIEW,

    advanced: {
        all: '',
        any: '',
        exclude: '',
        fields: ADVANCED_FIELDS,
    },
};

export function searchReducer(state: any = INITIAL_STATE, action: any) {
    if (!action) {
        return state;
    }

    switch (action.type) {

    case TOGGLE_NAVIGATION: {
        return {
            ...state,
            activeFilter: {},
            createdFilter: {},
            activeNavigation: get(action, 'navigation') || [],
        };
    }

    case TOGGLE_TOPIC: {
        const activeTopic = action.topic ? action.topic._id : null;

        return {
            ...state,
            activeFilter: {},
            createdFilter: {},
            activeTopic,
        };
    }

    case TOGGLE_FILTER: {
        const activeFilter = Object.assign({}, state.activeFilter);
        activeFilter[action.key] = toggleValue(activeFilter[action.key], action.val);
        if (!action.val || !activeFilter[action.key] || activeFilter[action.key].length === 0) {
            delete activeFilter[action.key];
        }
        else if (action.single) {
            activeFilter[action.key] = activeFilter[action.key].filter((val: any) => val === action.val);
        }
        return {
            ...state,
            activeFilter: activeFilter,
        };
    }

    case SET_CREATED_FILTER: {
        const createdFilter = Object.assign({}, state.createdFilter, action.filter);
        return {
            ...state,
            createdFilter,
        };
    }

    case RESET_FILTER:
        return {
            ...state,
            activeFilter: Object.assign({}, action.filter),
            createdFilter: {},
        };

    case SET_VIEW:
        return {
            ...state,
            activeView: action.view,
        };

    case SET_SEARCH_TOPIC_ID:
        return {
            ...state,
            activeTopic: action.payload,
        };

    case SET_SEARCH_NAVIGATION_IDS:
        return {
            ...state,
            activeNavigation: action.payload,
        };

    case SET_SEARCH_QUERY:
        return {
            ...state,
            activeQuery: action.payload,
        };

    case SET_SEARCH_FILTERS:
        return {
            ...state,
            activeFilter: action.payload,
        };

    case SET_SEARCH_CREATED:
        return {
            ...state,
            createdFilter: action.payload,
        };

    case SET_SEARCH_PRODUCT:
        return {
            ...state,
            productId: action.payload,
        };

    case RESET_SEARCH_PARAMS:
        return {
            ...state,
            activeTopic: INITIAL_STATE.activeTopic,
            activeNavigation: INITIAL_STATE.activeNavigation,
            activeQuery: INITIAL_STATE.activeQuery,
            activeFilter: INITIAL_STATE.activeFilter,
            createdFilter: INITIAL_STATE.createdFilter,
            productId: INITIAL_STATE.productId,
            advanced: {
                all: '',
                any: '',
                exclude: '',
                fields: ADVANCED_FIELDS,
            },
        };

    case TOGGLE_ADVANCED_SEARCH_FIELD:
        return {
            ...state,
            advanced: {
                ...state.advanced,
                fields: state.advanced.fields.includes(action.payload) ?
                    state.advanced.fields.filter((field: any) => field !== action.payload) :
                    [...state.advanced.fields, action.payload],
            },
        };

    case SET_ADVANCED_SEARCH_KEYWORDS:
        return {
            ...state,
            advanced: {
                ...state.advanced,
                [action.payload.field]: action.payload.keywords,
            },
        };

    case CLEAR_ADVANCED_SEARCH_PARAMS:
        return {
            ...state,
            advanced: {
                all: '',
                any: '',
                exclude: '',
                fields: ADVANCED_FIELDS,
            },
        };

    case SET_ADVANCED_SEARCH_PARAMS:
        return {
            ...state,
            advanced: {
                all: action.payload.all || '',
                any: action.payload.any || '',
                exclude: action.payload.exclude || '',
                fields: action.payload.fields || ADVANCED_FIELDS,
            },
        };

    default:
        return state;
    }
}
