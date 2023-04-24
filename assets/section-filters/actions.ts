import {initSections} from 'assets/features/sections/actions';
import {searchQuerySelector} from 'assets/search/selectors';
import server from 'assets/server';
import {errorHandler, gettext, notify} from 'assets/utils';


export const SELECT_SECTION_FILTER = 'SELECT_SECTION_FILTER';
export function selectSectionFilter(id: any): any {
    return {type: SELECT_SECTION_FILTER, id};
}

export const EDIT_SECTION_FILTER = 'EDIT_SECTION_FILTER';
export function editSectionFilter(event: any): any {
    return {type: EDIT_SECTION_FILTER, event};
}

export const NEW_SECTION_FILTER = 'NEW_SECTION_FILTER';
export function newSectionFilter(): any {
    return {type: NEW_SECTION_FILTER};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit(event: any): any {
    return {type: CANCEL_EDIT, event};
}

export const QUERY_SECTION_FILTERS = 'QUERY_SECTION_FILTERS';
export function querySectionFilters(): any {
    return {type: QUERY_SECTION_FILTERS};
}

export const GET_SECTION_FILTERS = 'GET_SECTION_FILTERS';
export function getSectionFilters(data: any): any {
    return {type: GET_SECTION_FILTERS, data};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any): any {
    return {type: SET_ERROR, errors};
}


/**
 * Fetches section Filters
 *
 */
export function fetchSectionFilters(): any {
    return function (dispatch: any, getState: any) {
        dispatch(querySectionFilters());
        const query = searchQuerySelector(getState()) || '';

        return server.get(`/section_filters/search?q=${query}`)
            .then((data: any) => dispatch(getSectionFilters(data)))
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}


/**
 * Creates new section filter
 *
 */
export function postSectionFilter(): any {
    return function (dispatch: any, getState: any) {

        const sectionFilter = getState().sectionFilterToEdit;
        const url = `/section_filters/${sectionFilter._id ? sectionFilter._id : 'new'}`;

        return server.post(url, sectionFilter)
            .then(function() {
                if (sectionFilter._id) {
                    notify.success(gettext('Section Filter updated successfully'));
                } else {
                    notify.success(gettext('Section Filter created successfully'));
                }
                dispatch(fetchSectionFilters());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));

    };
}


/**
 * Deletes a section filter
 *
 */
export function deleteSectionFilter(): any {
    return function (dispatch: any, getState: any) {

        const sectionFilter = getState().sectionFilterToEdit;
        const url = `/section_filters/${sectionFilter._id}`;

        return server.del(url)
            .then(() => {
                notify.success(gettext('Section Filter deleted successfully'));
                dispatch(fetchSectionFilters());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}




export function initViewData(data: any): any {
    return function (dispatch: any) {
        dispatch(getSectionFilters(data.section_filters));
        dispatch(initSections(data.sections));
    };
}
