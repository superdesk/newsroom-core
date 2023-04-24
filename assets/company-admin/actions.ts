import server from 'assets/server';
import {fetchUsers, initViewData as initUserViewData, setError} from 'assets/users/actions';
import {errorHandler, gettext, notify} from 'assets/utils';

export const INIT_VIEW_DATA = 'INIT_VIEW_DATA';
export function initViewData(data: any): any {
    return (dispatch: any) => {
        dispatch({type: INIT_VIEW_DATA, data: data});
        dispatch(initUserViewData(data));
    };
}

export const SET_SECTION = 'SET_SECTION';
export function setSection(id: any): any {
    return {type: SET_SECTION, id: id};
}

export const SET_PRODUCT_FILTER = 'SET_PRODUCT_FILTER';
export function setProductFilter(id: any): any {
    return function(dispatch: any) {
        dispatch({type: SET_PRODUCT_FILTER, id: id});
        dispatch(fetchUsers());
    };
}

export function sendProductSeatRequest(data: any): any {
    return function (dispatch: any) {
        return server.post('/company_admin/send_product_seat_request', data)
            .then(() => notify.success(gettext('Product Seat request sent')))
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}
