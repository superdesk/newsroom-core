import server from 'server';
import {errorHandler} from '../utils';
import {gettext, notify} from 'utils';

export const UPDATE_VALUES = 'UPDATE_VALUES';
function updateValues(data: any) {
    return {type: UPDATE_VALUES, data};
}

export function save(values: any) {
    return (dispatch: any) => {
        server.post('/settings/general_settings', values)
            .then((data: any) => {
                notify.success(gettext('Settings were updated successfully.'));
                dispatch(updateValues(data));
            }, (reason: any) => errorHandler(reason));
    };
}

export const INIT_VIEW_DATA = 'INIT_VIEW_DATA';
export function initViewData(data: any) {
    return {type: INIT_VIEW_DATA, data: data};
}
