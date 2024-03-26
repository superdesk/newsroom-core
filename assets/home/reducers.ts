
import {
    INIT_DATA,
    OPEN_ITEM,
    SET_ACTIVE,
    SET_CARD_ITEMS,
    SET_MULTIPLE_CARD_ITEMS,
} from './actions';
import {BOOKMARK_ITEMS, REMOVE_BOOKMARK} from '../wire/actions';
import {CLOSE_MODAL, MODAL_FORM_VALID, RENDER_MODAL, SET_USER} from '../actions';
import {IModalState, modalReducer} from '../reducers';
import {topicsReducer} from '../topics/reducer';
import {IArticle, IDashboardCard, IProduct, ITopic, IUser} from 'interfaces';
import {IHomeUIConfig} from 'interfaces/configs';

export interface IPersonalizedDashboardsWithData {
    dashboard_id?: string;
    dashboard_name?: string;
    topic_items?: Array<{_id: string, items: Array<any>}>;
}

export interface IPublicAppState {
    cards: Array<IDashboardCard>;
    itemsById: {[itemId: string]: IArticle};
    itemsByCard: {[cardId: string]: Array<IArticle>};
    uiConfig: IHomeUIConfig;
    modal?: IModalState;
}

export interface IHomeState extends IPublicAppState {
    personalizedDashboards?: Array<IPersonalizedDashboardsWithData>;
    topics?: Array<ITopic>;
    products?: Array<IProduct>;
    activeCard?: any;
    userProducts?: Array<any>;
    currentUser?: any;
    user?: IUser['_id'];
    userType?: IUser['user_type'];
    userSections?: IUser['sections']
    company?: IUser['company']
    itemToOpen?: IArticle;
    companyProducts?: Array<any>;
    context?: string;
    groups?: Array<any>;
    formats?: Array<any>;
}

const initialState: IHomeState = {
    cards: [],
    topics: [],
    products: [],
    itemsByCard: {},
    itemsById: {},
    activeCard: null,
    uiConfig: {_id: 'home'},
    userProducts: [],
    companyProducts: [],
    currentUser: {},
    personalizedDashboards: [],
    context: 'wire',
    formats: [],
    groups: [],
};

export default function homeReducer(state: IHomeState = initialState, action: any): IHomeState {

    switch (action.type) {

    case INIT_DATA:
        return {
            ...state,
            personalizedDashboards: action.data?.personalizedDashboards,
            cards: action.data.cards,
            itemsByCard: {},
            currentUser: action.data.currentUser,
            products: action.data.products,
            user: action.data.user,
            userType: action.data.userType,
            companyProducts: action.data.companyProducts,
            userProducts: action.data.userProducts,
            company: action.data.company,
            formats: action.data.formats || [],
            userSections: action.data.userSections,
            uiConfig: action.data.ui_config || {},
            topics: action.data.topics || [],
            context: 'wire',
            groups: action.data.groups || [],
        };

    case OPEN_ITEM:{
        return {
            ...state,
            itemToOpen: action.item || null,
        };
    }

    case SET_USER: {
        return {
            ...state,
            currentUser: action.data
        };
    }

    case SET_ACTIVE:
        return {
            ...state,
            activeCard: action.cardId || null,
        };

    case BOOKMARK_ITEMS: {
        const itemToOpen = Object.assign({}, state.itemToOpen);
        itemToOpen.bookmarks = (itemToOpen.bookmarks || []).concat([state.user ?? '']);

        return {
            ...state,
            itemToOpen,
        };
    }

    case REMOVE_BOOKMARK: {
        const itemToOpen = Object.assign({}, state.itemToOpen);
        itemToOpen.bookmarks = (itemToOpen.bookmarks || []).filter((val: any) => val !== state.user);

        return {
            ...state,
            itemToOpen,
        };
    }

    case SET_CARD_ITEMS: {
        const itemsById = {...state.itemsById};

        setItemsById(itemsById, action.payload.items);

        return {
            ...state,
            itemsById,
            itemsByCard: {
                ...state.itemsByCard,
                [action.payload.card]: action.payload.items,
            },
        };
    }

    case SET_MULTIPLE_CARD_ITEMS: {
        const itemsById = {...state.itemsById};

        for (const card in action.payload) {
            setItemsById(itemsById, action.payload[card]);
        }

        return {
            ...state,
            itemsById,
            itemsByCard: {
                ...state.itemsByCard,
                ...action.payload,
            },
        };
    }

    case RENDER_MODAL:
    case MODAL_FORM_VALID:
    case CLOSE_MODAL:
        return {...state, modal: modalReducer(state.modal, action)};

    default:
        return {...state, topics: topicsReducer(state.topics, action)};
    }
}

function setItemsById(itemsById: IHomeState['itemsById'], items: Array<IArticle>) {
    items.forEach((item: IArticle) => {
        itemsById[item._id] = item;
    });
}
