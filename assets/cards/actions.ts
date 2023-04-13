import {gettext, notify, errorHandler} from 'utils';
import server from 'server';
import {initDashboard} from 'features/dashboard/actions';
import {searchQuerySelector} from 'search/selectors';


export const SELECT_CARD = 'SELECT_CARD';
export function selectCard(id: any): any {
    return {type: SELECT_CARD, id};
}

export const EDIT_CARD = 'EDIT_CARD';
export function editCard(event: any): any {
    return {type: EDIT_CARD, event};
}

export const NEW_CARD = 'NEW_CARD';
export function newCard(): any {
    return {type: NEW_CARD};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit(event: any): any {
    return {type: CANCEL_EDIT, event};
}

export const QUERY_CARDS = 'QUERY_CARDS';
export function queryCards(): any {
    return {type: QUERY_CARDS};
}

export const GET_CARDS = 'GET_CARDS';
export function getCards(data: any): any {
    return {type: GET_CARDS, data};
}

export const GET_PRODUCTS = 'GET_PRODUCTS';
export function getProducts(data: any): any {
    return {type: GET_PRODUCTS, data};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any): any {
    return {type: SET_ERROR, errors};
}

export const GET_NAVIGATIONS = 'GET_NAVIGATIONS';
export function getNavigations(data: any): any {
    return {type: GET_NAVIGATIONS, data};
}

/**
 * Fetches cards
 *
 */
export function fetchCards(): any {
    return function (dispatch: any, getState: any) {
        dispatch(queryCards());
        const query = searchQuerySelector(getState()) || '';

        return server.get(`/cards/search?q=${query}`)
            .then((data) => dispatch(getCards(data)))
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Creates new cards
 *
 */
export function postCard(): any {
    return function (dispatch: any, getState: any) {

        const card = getState().cardToEdit;
        const data = new FormData();
        data.append('card', JSON.stringify(card));

        if (card.type === '4-photo-gallery') {
            const errors = {
                config: {
                    sources: [{}, {}, {}, {}]
                }
            };
            let errorFound = false;
            let mediaCount = 0;
            (card.config.sources || []).forEach((source, index) => {
                if (!source.url && parseInt(source.count, 10) > 0) {
                    errors.config.sources[index].url = gettext('Invalid Url.');
                    errorFound = true;
                }

                if (source.url && !source.count) {
                    errors.config.sources[index].count = gettext('Invalid count of media.');
                    errorFound = true;
                }

                if (parseInt(source.count, 10) > 0) {
                    mediaCount += parseInt(source.count, 10);
                } else if (parseInt(source.count, 10) <= 0) {
                    errors.config.sources[index].count = gettext('Count of media should be greater than zero.');
                    errorFound = true;
                }
            });

            if (mediaCount > 4 || mediaCount === 0) {
                notify.error(gettext('Total media count across all media config should be between 1 and 4.'));
                return;
            }

            if (errorFound) {
                notify.error(gettext('Failed to update Card.'));
                dispatch(setError(errors));
                return;
            }
        }

        if (card.type === '2x2-events') {
            [...Array(4)].forEach((_, i) => {
                const input = document.getElementById(`config.events[${i}].file`);
                if (input && input.files.length > 0) {
                    data.append(`file${i}`, input.files[0]);
                }
            });
        }

        const url = `/cards/${card._id ? card._id : 'new'}`;

        return server.postFiles(url, data)
            .then(function() {
                if (card._id) {
                    notify.success(gettext('Card updated successfully'));
                } else {
                    notify.success(gettext('Card created successfully'));
                }
                dispatch(fetchCards());
            })
            .catch((error) => errorHandler(error, dispatch, setError));

    };
}


/**
 * Deletes a card
 *
 */
export function deleteCard(): any {
    return function (dispatch: any, getState: any) {

        const card = getState().cardToEdit;
        const url = `/cards/${card._id}`;

        return server.del(url)
            .then(() => {
                notify.success(gettext('Card deleted successfully'));
                dispatch(fetchCards());
            })
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Fetches products
 *
 */
export function fetchProducts(): any {
    return function (dispatch: any) {
        return server.get('/products/search')
            .then((data) => {
                dispatch(getProducts(data));
            })
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}


export function initViewData(data: any): any {
    return function (dispatch: any) {
        dispatch(getCards(data.cards));
        dispatch(getProducts(data.products));
        dispatch(getNavigations(data.navigations));
        dispatch(initDashboard(data.dashboards));
    };
}

