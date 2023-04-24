import server from 'assets/server';
import {gettext, notify} from 'assets/utils';
import {errorHandler} from '../utils';

export const UPDATE_VALUES = 'UPDATE_VALUES';
function updateValues(data: any): any {
    return {type: UPDATE_VALUES, data};
}

export function save(values: any): any {
    return (dispatch: any) => {
        server.post('/settings/general_settings', values)
            .then((data: any) => {
                notify.success(gettext('Settings were updated successfully.'));
                dispatch(updateValues(data));
            }, (reason: any) => errorHandler(reason));
    };
}

export const INIT_VIEW_DATA = 'INIT_VIEW_DATA';
export function initViewData(data: any): any {
    return {type: INIT_VIEW_DATA, data: data};
}
