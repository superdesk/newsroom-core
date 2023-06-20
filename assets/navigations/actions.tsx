import {gettext, notify, errorHandler} from 'utils';
import server from 'server';
import {initSections} from 'features/sections/actions';
import {activeSectionSelector} from 'features/sections/selectors';
import {searchQuerySelector} from 'search/selectors';

// number of image that a navigation can have
export const MAX_TILE_IMAGES = 4;

export const SELECT_NAVIGATION = 'SELECT_NAVIGATION';
export function selectNavigation(id: any) {
    return {type: SELECT_NAVIGATION, id};
}

export const EDIT_NAVIGATION = 'EDIT_NAVIGATION';
export function editNavigation(event: any) {
    return {type: EDIT_NAVIGATION, event};
}

export const NEW_NAVIGATION = 'NEW_NAVIGATION';
export function newNavigation() {
    return {type: NEW_NAVIGATION};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit(event: any) {
    return {type: CANCEL_EDIT, event};
}

export const QUERY_NAVIGATIONS = 'QUERY_NAVIGATIONS';
export function queryNavigations() {
    return {type: QUERY_NAVIGATIONS};
}

export const GET_NAVIGATIONS = 'GET_NAVIGATIONS';
export function getNavigations(data: any) {
    return {type: GET_NAVIGATIONS, data};
}

export const GET_PRODUCTS = 'GET_PRODUCTS';
export function getProducts(data: any) {
    return {type: GET_PRODUCTS, data};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any) {
    return {type: SET_ERROR, errors};
}


/**
 * Fetches navigations
 *
 */
export function fetchNavigations() {
    return function (dispatch: any, getState: any) {
        dispatch(queryNavigations());
        const query = searchQuerySelector(getState()) || '';

        return server.get(`/navigations/search?q=${query}`)
            .then((data: any) => dispatch(getNavigations(data)))
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Creates new navigations
 *
 */
export function postNavigation() {
    return function (dispatch: any, getState: any) {

        const navigation = getState().navigationToEdit;
        if (!navigation._id) {
            // set the action section for new navigation
            navigation.product_type = activeSectionSelector(getState());
        }

        const url = `/navigations/${navigation._id ? navigation._id : 'new'}`;
        let data = new FormData();

        data.append('navigation', JSON.stringify(navigation));
        for(let i = 0; i < MAX_TILE_IMAGES; i++) {
            const fileInput: any = document.getElementById(`tile_images_file_${i}`);
            if (fileInput && fileInput.files.length > 0) {
                data.append(`file${i}`, fileInput.files[0]);
            }
        }

        return server.postFiles(url, data)
            .then(function() {
                if (navigation._id) {
                    notify.success(gettext('Navigation updated successfully'));
                } else {
                    notify.success(gettext('Navigation created successfully'));
                }
                dispatch(fetchNavigations());
                dispatch(fetchProducts());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));

    };
}


/**
 * Deletes a navigation
 *
 */
export function deleteNavigation() {
    return function (dispatch: any, getState: any) {

        const navigation = getState().navigationToEdit;
        const url = `/navigations/${navigation._id}`;

        return (server as any).del(url)
            .then(() => {
                notify.success(gettext('Navigation deleted successfully'));
                dispatch(fetchNavigations());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Fetches products
 *
 */
export function fetchProducts() {
    return function (dispatch: any) {
        return server.get('/products/search')
            .then((data: any) => {
                dispatch(getProducts(data));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function initViewData(data: any): any {
    return function (dispatch: any) {
        dispatch(getNavigations(data.navigations));
        dispatch(getProducts(data.products));
        dispatch(initSections(data.sections));
    };
}

