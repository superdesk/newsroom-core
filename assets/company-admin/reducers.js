import {INIT_VIEW_DATA, SET_PRODUCT_FILTER, SET_SECTION} from './actions';

import {RENDER_MODAL, CLOSE_MODAL, MODAL_FORM_VALID, MODAL_FORM_INVALID} from 'actions';
import {modalReducer} from 'reducers';
import {searchReducer} from 'search/reducers';
import userReducer from 'users/reducers';

const initialState = {
    user: null,
    query: null,
    users: [],
    usersById: {},
    activeUserId: null,
    isLoading: false,
    totalUsers: null,
    activeQuery: null,
    companies: [],
    company: null,
    sort: null,
    sortDirection: 1,
    modal: modalReducer(),
    search: searchReducer(undefined, undefined, 'settings'),

    userToEdit: null,
    errors: null,

    sectionId: 'my_company',
    sections: [],
    products: [],
    productId: null,
};

export function companyAdminReducer(state = initialState, action) {
    switch (action.type) {
    case INIT_VIEW_DATA:
        return {
            ...userReducer(state, action),
            products: action.data.products,
            company: action.data.companyId,
        };
    case SET_PRODUCT_FILTER:
        return {
            ...state,
            productId: action.id,
        };
    case SET_SECTION:
        return {
            ...state,
            sectionId: action.id,
        };

    case RENDER_MODAL:
    case CLOSE_MODAL:
    case MODAL_FORM_VALID:
    case MODAL_FORM_INVALID:
        return {...state, modal: modalReducer(state.modal, action)};

    default:
        return userReducer(state, action);
    }
}
