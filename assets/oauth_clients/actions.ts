import {gettext, notify, errorHandler} from 'utils';
import server from 'server';
import {searchQuerySelector} from 'search/selectors';


export const SELECT_CLIENT = 'SELECT_CLIENT';
export function selectClient(id: any): any {
    return function (dispatch: any) {
        dispatch(select(id));
    };
}

function select(id: any): any {
    return {type: SELECT_CLIENT, id};
}

export const EDIT_CLIENT = 'EDIT_CLIENT';
export function editClient(event: any): any {
    return {type: EDIT_CLIENT, event};
}

export const NEW_CLIENT = 'NEW_CLIENT';
export function newClient(data: any): any {
    return {type: NEW_CLIENT, data};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit(event: any): any {
    return {type: CANCEL_EDIT, event};
}

export const QUERY_CLIENTS = 'QUERY_CLIENTS';
export function queryClients(): any {
    return {type: QUERY_CLIENTS};
}

export const GET_CLIENTS = 'GET_CLIENTS';
export function getClients(data: any): any {
    return {type: GET_CLIENTS, data};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any): any {
    return {type: SET_ERROR, errors};
}


export const GET_CLIENT_PASSWORD = 'GET_CLIENT_PASSWORD';
export function getClientPassword(data: any): any {
    return {type: GET_CLIENT_PASSWORD, data};
}


/**
 * Fetches clients
 *
 */
export function fetchClients(): any {
    return function (dispatch: any, getState: any) {
        dispatch(queryClients());
        const query = searchQuerySelector(getState()) || '';

        return server.get(`/oauth_clients/search?q=${query}`)
            .then((data) => {
                dispatch(getClients(data));
            })
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Creates new client
 *
 */
export function postClient(): any {
    return function (dispatch: any, getState: any) {
        const client = getState().clientToEdit;
        const url = `/oauth_clients/${client._id ? client._id : 'new'}`;

        return server.post(url, client)
            .then((data) => {
                if (client._id) {
                    notify.success(gettext('Client updated successfully'));
                } else {
                    dispatch(getClientPassword(data));
                    notify.success(gettext('Client created successfully'));
                }
                dispatch(fetchClients());
            })
            .catch((error) => errorHandler(error, dispatch, setError));

    };
}


/**
 * Deletes a client
 *
 */
export function deleteClient(): any {
    return function (dispatch: any, getState: any) {

        const client = getState().clientToEdit;
        const url = `/oauth_clients/${client._id}`;

        return server.del(url)
            .then(() => {
                notify.success(gettext('Client deleted successfully'));
                dispatch(fetchClients());
            })
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}

export const INIT_VIEW_DATA = 'INIT_VIEW_DATA';
export function initViewData(data: any): any {
    return {type: INIT_VIEW_DATA, data};
}
