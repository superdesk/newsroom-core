import {gettext, notify, errorHandler} from 'utils';
import server from 'server';
import {initSections} from 'features/sections/actions';
import {searchQuerySelector} from 'search/selectors';


export const SELECT_PRODUCT = 'SELECT_PRODUCT';
export function selectProduct(id: any) {
    return {type: SELECT_PRODUCT, id};
}

export const EDIT_PRODUCT = 'EDIT_PRODUCT';
export function editProduct(event: any) {
    return {type: EDIT_PRODUCT, event};
}

export const NEW_PRODUCT = 'NEW_PRODUCT';
export function newProduct() {
    return {type: NEW_PRODUCT};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit(event: any) {
    return {type: CANCEL_EDIT, event};
}

export const QUERY_PRODUCTS = 'QUERY_PRODUCTS';
export function queryProducts() {
    return {type: QUERY_PRODUCTS};
}

export const GET_PRODUCTS = 'GET_PRODUCTS';
export function getProducts(data: any) {
    return {type: GET_PRODUCTS, data};
}

export const GET_COMPANIES = 'GET_COMPANIES';
export function getCompanies(data: any) {
    return {type: GET_COMPANIES, data};
}

export const GET_NAVIGATIONS = 'GET_NAVIGATIONS';
export function getNavigations(data: any) {
    return {type: GET_NAVIGATIONS, data};
}

export const UPDATE_PRODUCT_NAVIGATIONS = 'UPDATE_PRODUCT_NAVIGATIONS';
export function updateProductNavigations(product: any, navigations: any) {
    return {type: UPDATE_PRODUCT_NAVIGATIONS, product, navigations};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any) {
    return {type: SET_ERROR, errors};
}


/**
 * Fetches products
 *
 */
export function fetchProducts() {
    return function (dispatch: any, getState: any) {
        dispatch(queryProducts());
        const query = searchQuerySelector(getState()) || '';

        return server.get(`/products/search?q=${query}`)
            .then((data: any) => dispatch(getProducts(data)))
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Creates new products
 *
 */
export function postProduct(): any {
    return function (dispatch: any, getState: any) {

        const product = getState().productToEdit;
        const url = `/products/${product._id ? product._id : 'new'}`;

        return server.post(url, product)
            .then(function() {
                if (product._id) {
                    notify.success(gettext('Product updated successfully'));
                } else {
                    notify.success(gettext('Product created successfully'));
                }
                dispatch(fetchProducts());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));

    };
}


/**
 * Deletes a product
 *
 */
export function deleteProduct() {
    return function (dispatch: any, getState: any) {

        const product = getState().productToEdit;
        const url = `/products/${product._id}`;

        return (server as any).del(url)
            .then(() => {
                notify.success(gettext('Product deleted successfully'));
                dispatch(fetchProducts());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Fetches companies
 *
 */
export function fetchCompanies() {
    return function (dispatch: any) {
        return server.get('/companies/search')
            .then((data: any) => {
                dispatch(getCompanies(data));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Saves companies for a product
 *
 */
export function saveCompanies(companies: any) {
    return function (dispatch: any, getState: any) {
        const product = getState().productToEdit;
        return server.post(`/products/${product._id}/companies`, {companies})
            .then(() => {
                notify.success(gettext('Product updated successfully'));
                dispatch(fetchCompanies());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Fetches navigations
 *
 */
export function fetchNavigations() {
    return function (dispatch: any) {
        return server.get('/navigations/search')
            .then((data: any) => {
                dispatch(getNavigations(data));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Saves navigations for a product
 *
 */
export function saveNavigations(navigations: any) {
    return function (dispatch: any, getState: any) {
        const product = getState().productToEdit;
        return server.post(`/products/${product._id}/navigations`, {navigations})
            .then(() => {
                notify.success(gettext('Product updated successfully'));
                dispatch(updateProductNavigations(product, navigations));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function initViewData(data: any): any {
    return function (dispatch: any) {
        dispatch(getProducts(data.products));
        dispatch(getCompanies(data.companies));
        dispatch(getNavigations(data.navigations));
        dispatch(initSections(data.sections));
    };
}
