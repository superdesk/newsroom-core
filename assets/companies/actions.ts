import {gettext, notify, errorHandler} from 'utils';
import server from 'server';
import {searchQuerySelector} from 'search/selectors';


export const SELECT_COMPANY = 'SELECT_COMPANY';
export function selectCompany(id: any): any {
    return function (dispatch: any) {
        dispatch(select(id));
        dispatch(fetchCompanyUsers(id));
    };
}

function select(id: any): any {
    return {type: SELECT_COMPANY, id};
}

export const EDIT_COMPANY = 'EDIT_COMPANY';
export function editCompany(event: any): any {
    return {type: EDIT_COMPANY, event};
}

export const NEW_COMPANY = 'NEW_COMPANY';
export function newCompany(data: any): any {
    return {type: NEW_COMPANY, data};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit(event: any): any {
    return {type: CANCEL_EDIT, event};
}

export const QUERY_COMPANIES = 'QUERY_COMPANIES';
export function queryCompanies(): any {
    return {type: QUERY_COMPANIES};
}

export const GET_COMPANIES = 'GET_COMPANIES';
export function getCompanies(data: any): any {
    return {type: GET_COMPANIES, data};
}

export const GET_COMPANY_USERS = 'GET_COMPANY_USERS';
export function getCompanyUsers(data: any): any {
    return {type: GET_COMPANY_USERS, data};
}

export const GET_PRODUCTS = 'GET_PRODUCTS';
export function getProducts(data: any): any {
    return {type: GET_PRODUCTS, data};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any): any {
    return {type: SET_ERROR, errors};
}


/**
 * Fetches companies
 *
 */
export function fetchCompanies(): any {
    return function (dispatch: any, getState: any) {
        dispatch(queryCompanies());
        const query = searchQuerySelector(getState()) || '';

        return server.get(`/companies/search?q=${query}`)
            .then((data: any) => {
                dispatch(getCompanies(data));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Fetches users of a company
 *
 * @param {String} companyId
 */
export function fetchCompanyUsers(companyId: any,  force = false): any {
    return function (dispatch: any, getState: any) {
        if (!force && !getState().companiesById[companyId].name) {
            return;
        }

        return server.get(`/companies/${companyId}/users`)
            .then((data: any) => {
                return dispatch(getCompanyUsers(data));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Creates new company
 *
 */
export function postCompany(permissions = null): any {
    return function (dispatch: any, getState: any) {

        const company = getState().companyToEdit;
        const url = `/companies/${company._id ? company._id : 'new'}`;

        return (permissions == null ?
            Promise.resolve() :
            dispatch(savePermissions(company, permissions))
        ).then(() => {
            return server.post(url, company)
                .then(function() {
                    if (company._id) {
                        notify.success(gettext('Company updated successfully'));
                    } else {
                        notify.success(gettext('Company created successfully'));
                    }
                    dispatch(fetchProducts());
                    dispatch(fetchCompanies());
                })
                .catch((error: any) => errorHandler(error, dispatch, setError));
        });
    };
}


/**
 * Fetches products
 *
 */
export function fetchProducts(): any {
    return function (dispatch: any) {
        return server.get('/products/search')
            .then((data: any) => {
                dispatch(getProducts(data));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Save permissions for a company
 *
 */
export function savePermissions(company: any, permissions: any): any {
    return function (dispatch: any) {
        return server.post(`/companies/${company._id}/permissions`, permissions)
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Deletes a company
 *
 */
export function deleteCompany(): any {
    return function (dispatch: any, getState: any) {

        const company = getState().companyToEdit;
        const url = `/companies/${company._id}`;

        return server.del(url)
            .then(() => {
                notify.success(gettext('Company deleted successfully'));
                dispatch(fetchCompanies());
            })
            .catch((error: any) => {
                if (error.response.status == 403) {
                    error.response.json().then(function(data) {
                        notify.error(data['error']);
                    });
                }
                errorHandler(error, dispatch, setError);
            });
    };
}

export const INIT_VIEW_DATA = 'INIT_VIEW_DATA';
export function initViewData(data: any): any {
    return {type: INIT_VIEW_DATA, data};
}
