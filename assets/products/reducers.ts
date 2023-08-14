import {
    GET_PRODUCTS,
    SELECT_PRODUCT,
    EDIT_PRODUCT,
    QUERY_PRODUCTS,
    CANCEL_EDIT,
    NEW_PRODUCT,
    SET_ERROR,
    GET_COMPANIES,
    GET_NAVIGATIONS,
    UPDATE_PRODUCT_NAVIGATIONS,
} from './actions';
import {ADD_EDIT_USERS} from 'actions';

import {INIT_SECTIONS, SELECT_SECTION} from 'features/sections/actions';
import {sectionsReducer} from 'features/sections/reducers';
import {searchReducer} from 'search/reducers';

const initialState: any = {
    query: null,
    products: [],
    productsById: {},
    activeProductId: null,
    isLoading: false,
    totalProducts: null,
    activeQuery: null,
    companies: [],
    navigations: [],
    sections: sectionsReducer(),
    search: searchReducer(undefined, undefined, 'settings'),
};

export default function productReducer(state: any = initialState, action: any) {
    switch (action.type) {

    case SELECT_PRODUCT: {
        const defaultProduct: any = {
            is_enabled: true,
            name: '',
            description: '',
        };

        return {
            ...state,
            activeProductId: action.id || null,
            productToEdit: action.id ? Object.assign(defaultProduct, state.productsById[action.id]) : null,
            errors: null,
        };
    }

    case EDIT_PRODUCT: {
        const target = action.event.target;
        const field = target.name;
        const product = state.productToEdit;
        product[field] = target.type === 'checkbox' ? target.checked : target.value;
        return {...state, productToEdit: product, errors: null};
    }

    case NEW_PRODUCT: {
        const productToEdit: any = {
            is_enabled: true,
            name: '',
            description: '',
            product_type: state.sections.active,
        };

        return {...state, productToEdit, errors: null};
    }

    case CANCEL_EDIT: {
        return {...state, productToEdit: null, errors: null};
    }

    case SET_ERROR:
        return {...state, errors: action.errors};

    case QUERY_PRODUCTS:
        return {...state,
            isLoading: true,
            totalProducts: null,
            productToEdit: null,
            activeQuery: state.query};

    case GET_PRODUCTS: {
        const productsById = Object.assign({}, state.productsById);
        const products = action.data.map((product: any) => {
            productsById[product._id] = product;
            return product._id;
        });

        return {
            ...state,
            products,
            productsById,
            isLoading: false,
            totalProducts: products.length,
        };
    }

    case GET_COMPANIES: {
        const companiesById: any = {};
        action.data.map((company: any) => companiesById[company._id] = company);

        return {...state, companies: action.data, companiesById};
    }

    case GET_NAVIGATIONS: {
        const navigationsById: any = {};
        action.data.map((navigation: any) => navigationsById[navigation._id] = navigation);

        return {...state, navigations: action.data, navigationsById};
    }

    case UPDATE_PRODUCT_NAVIGATIONS: {
        const product = Object.assign({}, action.product, {navigations: action.navigations});
        const productsById = Object.assign({}, state.productsById);
        productsById[action.product._id] = product;

        return {...state, productsById, productToEdit: product};
    }

    case INIT_SECTIONS:
    case SELECT_SECTION:
        return {...state, sections: sectionsReducer(state.sections, action)};

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
