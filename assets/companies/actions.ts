import {ICompany} from 'interfaces';
import {gettext, notify, errorHandler, updateRouteParams} from 'utils';
import server from 'server';
import {searchQuerySelector} from 'search/selectors';
import {ICompanySettingsStore} from './reducers';


export const SELECT_COMPANY = 'SELECT_COMPANY';
export function selectCompany(id: string, updateRoute = true) {
    return function (dispatch: any) {
        if (updateRoute) {
            updateRouteParams({companyId: id}, {});
        }

        dispatch(select(id));
        dispatch(fetchCompanyUsers(id));
    };
}

function select(id: any) {
    return {type: SELECT_COMPANY, id};
}

export const EDIT_COMPANY = 'EDIT_COMPANY';
export function editCompany(event: any) {
    return {type: EDIT_COMPANY, event};
}

export const TOGGLE_COMPANY_SECTION = 'TOGGLE_COMPANY_SECTION';
export function toggleCompanySection(sectionId: any) {
    return {type: TOGGLE_COMPANY_SECTION, sectionId: sectionId};
}

export const TOGGLE_COMPANY_PRODUCT = 'TOGGLE_COMPANY_PRODUCT';
export function toggleCompanyProduct(productId: any, sectionId: any, enable: any) {
    return {type: TOGGLE_COMPANY_PRODUCT, payload: {
        productId: productId,
        sectionId: sectionId,
        enable: enable,
    }};
}

export const UPDATE_COMPANY_SEATS = 'UPDATE_COMPANY_SEATS';
export function updateCompanySeats(productId: any, seats: any) {
    return {type: UPDATE_COMPANY_SEATS, payload: {
        productId: productId,
        seats: seats,
    }};
}

export const NEW_COMPANY = 'NEW_COMPANY';
export function newCompany(data: any) {
    return {type: NEW_COMPANY, data};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit(event?: any, updateRoute = true) {
    if (updateRoute) {
        updateRouteParams({companyId: null}, {});
    }

    return {type: CANCEL_EDIT, event};
}

export const QUERY_COMPANIES = 'QUERY_COMPANIES';
export function queryCompanies() {
    return {type: QUERY_COMPANIES};
}

export const GET_COMPANIES = 'GET_COMPANIES';
export function getCompanies(data: any) {
    return {type: GET_COMPANIES, data};
}

export const GET_COMPANY_USERS = 'GET_COMPANY_USERS';
export function getCompanyUsers(data: any) {
    return {type: GET_COMPANY_USERS, data};
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
 * Fetches companies
 *
 */
export function fetchCompanies() {
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
export function fetchCompanyUsers(companyId: any, force: any = false) {
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

export function approveCompany(companyId: ICompany['_id']) {
    return function (dispatch: any) {
        return server.post(`/companies/${companyId}/approve`, {})
            .then(() => {
                notify.success(gettext('Company has been approved'));
                dispatch(fetchCompanies());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Creates new company
 *
 */
export function postCompany() {
    return function (dispatch: any, getState: any) {
        const company = getState().companyToEdit;
        const url = `/companies/${company._id ? company._id : 'new'}`;

        return server.post(url, company)
            .then(function () {
                if (company._id) {
                    notify.success(gettext('Company updated successfully'));
                } else {
                    notify.success(gettext('Company created successfully'));
                }
                dispatch(fetchProducts());
                dispatch(fetchCompanies());
                dispatch(cancelEdit());
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


/**
 * Deletes a company
 *
 */
export function deleteCompany() {
    return function (dispatch: any, getState: any) {

        const company = getState().companyToEdit;
        const url = `/companies/${company._id}`;

        return (server as any).del(url)
            .then(() => {
                notify.success(gettext('Company deleted successfully'));
                dispatch(fetchCompanies());
            })
            .catch((error: any) => {
                if (error.response.status == 403) {
                    error.response.json().then(function(data: any) {
                        notify.error(data['error']);
                    });
                }
                errorHandler(error, dispatch, setError);
            });
    };
}

export const INIT_VIEW_DATA = 'INIT_VIEW_DATA';
export function initViewData(data: any) {
    return {type: INIT_VIEW_DATA, data};
}

export function onURLParamsChanged() {
    return (dispatch: any, getState: any) => {
        const params = new URLSearchParams(window.location.search);
        const companyId = params.get('companyId');
        const state: ICompanySettingsStore = getState();

        if (companyId != null && state.companyToEdit?._id !== companyId) {
            dispatch(selectCompany(companyId, false));
        } else if (companyId == null && state.companyToEdit != null) {
            dispatch(cancelEdit(undefined, false));
        }
    };
}
