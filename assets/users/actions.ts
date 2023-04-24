import {searchQuerySelector} from 'assets/search/selectors';
import server from 'assets/server';
import {errorHandler, gettext, notify} from 'assets/utils';
import {cloneDeep, get} from 'lodash';

export const SELECT_USER = 'SELECT_USER';
export function selectUser(id: any): any {
    return function (dispatch: any) {
        dispatch(select(id));
    };
}

function select(id: any): any {
    return {type: SELECT_USER, id};
}

export const GET_USER = 'GET_USER';
export function getUser(user: any): any {
    return {type: GET_USER, user};
}

export const EDIT_USER = 'EDIT_USER';
export function editUser(event: any): any {
    return {type: EDIT_USER, event};
}

export const NEW_USER = 'NEW_USER';
export function newUser(data: any): any {
    return {type: NEW_USER, data};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit(event: any): any {
    return {type: CANCEL_EDIT, event};
}

export const QUERY_USERS = 'QUERY_USERS';
export function queryUsers(): any {
    return {type: QUERY_USERS};
}

export const GET_USERS = 'GET_USERS';
export function getUsers(data: any): any {
    return {type: GET_USERS, data};
}

export const REMOVE_USER = 'REMOVE_USER';
function removeUser(userId: any): any {
    return {type: REMOVE_USER, userId: userId};
}

export const GET_COMPANIES = 'GET_COMPANIES';
export function getCompanies(data: any): any {
    return {type: GET_COMPANIES, data};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any): any {
    return {type: SET_ERROR, errors};
}

export const SET_COMPANY = 'SET_COMPANY';
export function setCompany(company: any): any {
    return {type: SET_COMPANY, company};
}

export const SET_SORT = 'SET_SORT';
export function setSort(param: any): any {
    return {type: SET_SORT, param};
}

export const TOGGLE_SORT_DIRECTION = 'TOGGLE_SORT_DIRECTION';
export function toggleSortDirection(): any {
    return {type: TOGGLE_SORT_DIRECTION};
}

/**
 * Fetches users
 *
 */
export function fetchUsers(): any {
    return function (dispatch: any, getState: any) {
        dispatch(queryUsers());
        const state = getState();
        const query = searchQuerySelector(state) || '';
        const filterQuery: any = {};

        if (state.company && state.company !== '') {
            filterQuery.company = state.company;
        }
        if (state.productId && state.productId !== '') {
            filterQuery['products._id'] = state.productId;
        }

        let filter = '';
        if (Object.keys(filterQuery).length) {
            filter = '&where=' + encodeURIComponent(JSON.stringify(filterQuery));
        }

        const sortField = state.sort || 'first_name';
        const sort = sortField === 'first_name' ?
            `&sort=[("${sortField}", ${getState().sortDirection})]` :
            `&sort=[("${sortField}", ${getState().sortDirection}), ("first_name", 1)]`;

        return server.get(`/users/search?q=${query}${filter}${sort}`)
            .then((data: any) => dispatch(getUsers(data)))
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Creates new users
 *
 */
export function postUser(): any {
    return function (dispatch: any, getState: any) {

        const user = cloneDeep(getState().userToEdit);
        const url = `/users/${user._id ? user._id : 'new'}`;

        if (user.sections != null) {
            user.sections = Object.keys(user.sections)
                .filter((sectionId: any) => user.sections[sectionId] === true)
                .join(',');
        }
        if (user.products != null) {
            user.products = user.products
                .map((product: any) => product._id)
                .join(',');
        }

        return server.post(url, user)
            .then(function() {
                if (user._id) {
                    notify.success(gettext('User updated successfully'));
                } else {
                    notify.success(gettext('User created successfully'));
                }
                dispatch(fetchUsers());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));

    };
}


export function resetPassword(): any {
    return function (dispatch: any, getState: any) {

        const user = getState().userToEdit;
        const url = `/users/${user._id}/reset_password`;

        return server.post(url, {})
            .then(() => notify.success(gettext('Reset password token is sent successfully')))
            .catch((error: any) => errorHandler(error, dispatch, setError));

    };
}

/**
 * Deletes a user
 *
 */
export function deleteUser(): any {
    return function (dispatch: any, getState: any) {

        const user = getState().userToEdit;
        const userId = user._id;
        const url = `/users/${userId}`;

        return server.del(url)
            .then(() => {
                notify.success(gettext('User deleted successfully'));
                dispatch(removeUser(userId));
                dispatch(fetchUsers());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function resendUserInvite(): any {
    return function(dispatch: any, getState: any) {
        const user = getState().userToEdit;
        const url = `/users/${user._id}/resend_invite`;

        return server.post(url, {})
            .then(() => notify.success(gettext('Invitation as been resent')))
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export const INIT_VIEW_DATA = 'INIT_VIEW_DATA';
export function initViewData(data: any): any {
    return function (dispatch: any) {
        dispatch({type: INIT_VIEW_DATA, data});
        dispatch(getUsers(data.users));
        dispatch(getCompanies(data.companies));
        dispatch(getUser(get(window.profileData, 'user', {})));
    };
}
