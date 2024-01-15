import {set, get} from 'lodash';

import {
    GET_CARDS,
    SELECT_CARD,
    EDIT_CARD,
    QUERY_CARDS,
    CANCEL_EDIT,
    NEW_CARD,
    SET_ERROR,
    GET_PRODUCTS,
    GET_NAVIGATIONS,
} from './actions';
import {INIT_DASHBOARD, SELECT_DASHBOARD} from 'features/dashboard/actions';
import {ADD_EDIT_USERS} from 'actions';
import {dashboardReducer} from 'features/dashboard/reducers';
import {searchReducer} from 'search/reducers';
import {getCard} from 'components/cards/utils';


const initialState: any = {
    query: null,
    cards: [],
    cardsById: {},
    activeCardId: null,
    isLoading: false,
    totalCards: null,
    activeQuery: null,
    products: [],
    navigations: [],
    dashboards: dashboardReducer(),
    search: searchReducer(undefined, undefined, 'settings'),
};

export default function cardReducer(state: any = initialState, action: any) {
    switch (action.type) {

    case SELECT_CARD: {
        const defaultCard: any = {
            label: '',
            type: '',
            config: {},
        };

        return {
            ...state,
            activeCardId: action.id || null,
            cardToEdit: action.id ? Object.assign(defaultCard, state.cardsById[action.id]) : null,
            errors: null,
        };
    }

    case EDIT_CARD: {
        const target = action.event.target;
        const field = target.name;
        const card: any = {...state.cardToEdit};
        const size: number = field === 'size' ?
            parseInt(target.value, 10) :
            card.config?.size ?? getCard(card.type)?.size ?? 0;

        if (!card.dashboard) {
            card.dashboard = 'newsroom';
        }

        if (field === 'type') {
            if (target.value === '2x2-events') {
                card['config'] = {events: [{}, {}, {}, {}]};
            } else if (target.value === '4-photo-gallery') {
                card['config'] = {sources: [{}, {}, {}, {}]};
            } else {
                card['config'] = {};
            }

            card[field] = target.value;

        } else if (field === 'product') {
            set(card, 'config.product', target.value);
        } else if (field.indexOf('event') >= 0) {
            if (get(card, 'config.events.length', 0) < size) {
                card.config.events = [{}, {}, {}, {}];
            }
            set(card, field, target.value);
        } else if (field.indexOf('source') >= 0) {
            if (get(card, 'config.sources.length', 0) < size) {
                card.config.sources = [{}, {}, {}, {}];
            }
            set(card, field, target.value);
        } else {
            set(card, field, target.value);
        }

        card['config']['size'] = size;

        return {...state, cardToEdit: card, errors: null};
    }

    case NEW_CARD: {
        const cardToEdit: any = {
            label: '',
            type: '',
            config: {},
            dashboard: state.dashboards.active,
        };

        return {...state, cardToEdit, errors: null};
    }

    case CANCEL_EDIT: {
        return {...state, cardToEdit: null, errors: null};
    }

    case SET_ERROR:
        return {...state, errors: action.errors};

    case QUERY_CARDS:
        return {...state,
            isLoading: true,
            totalCards: null,
            cardToEdit: null,
            activeQuery: state.query};

    case GET_CARDS: {
        const cardsById = Object.assign({}, state.cardsById);
        const cards = action.data.map((card: any) => {
            cardsById[card._id] = card;
            return card._id;
        });

        return {
            ...state,
            cards,
            cardsById,
            isLoading: false,
            totalCards: cards.length,
        };
    }

    case GET_PRODUCTS: {
        return {...state, products: action.data};
    }

    case GET_NAVIGATIONS: {
        return {...state, navigations: action.data};
    }

    case INIT_DASHBOARD:
    case SELECT_DASHBOARD:
        return {...state, dashboards: dashboardReducer(state.dashboards, action)};

    case ADD_EDIT_USERS: {
        return {
            ...state,
            editUsers: [
                ...(state.editUsers || []),
                ...action.data,
            ]
        };
    }

    default: {
        const search = searchReducer(state.search, action, 'settings');

        if (search !== state.search) {
            return {...state, search};
        }

        return state;
    }
    }
}
