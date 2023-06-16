import {gettext, notify, errorHandler} from 'utils';
import server from 'server';
import {initViewData as initUserViewData, setError, fetchUsers} from 'users/actions';

export const INIT_VIEW_DATA = 'INIT_VIEW_DATA';
export function initViewData(data: any) {
    return (dispatch: any) => {
        dispatch({type: INIT_VIEW_DATA, data: data});
        dispatch(initUserViewData(data));
    };
}

export const SET_SECTION = 'SET_SECTION';
export function setSection(id: any) {
    return {type: SET_SECTION, id: id};
}

export const SET_PRODUCT_FILTER = 'SET_PRODUCT_FILTER';
export function setProductFilter(id: any) {
    return function(dispatch) {
        dispatch({type: SET_PRODUCT_FILTER, id: id});
        dispatch(fetchUsers());
    };
}

export function sendProductSeatRequest(data: any) {
    return function (dispatch) {
        return server.post('/company_admin/send_product_seat_request', data)
            .then(() => notify.success(gettext('Product Seat request sent')))
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}
