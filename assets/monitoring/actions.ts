import server from 'assets/server';
import {errorHandler, gettext, notify} from 'assets/utils';
import {get} from 'lodash';
import {company, monitoringProfileToEdit, scheduleMode} from './selectors';


export const INIT_DATA = 'INIT_DATA';
export function initData(data: any): any {
    return {type: INIT_DATA, data};
}

export const SET_COMPANIES = 'SET_COMPANIES';
export function setCompanies(data: any): any {
    return {type: SET_COMPANIES, data};
}

export function initViewData(data: any): any {
    return function (dispatch: any) {
        dispatch(setCompanies(data.companies));
    };
}

export const NEW_MONITORING_PROFILE = 'NEW_MONITORING_PROFILE';
export function newMonitoringProfile(): any {
    return {type: NEW_MONITORING_PROFILE};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit(): any {
    return {type: CANCEL_EDIT};
}

export const UPDATE_MONITORING_PROFILE = 'UPDATE_MONITORING_PROFILE';
export function updateMonitoringProfile(event: any): any {
    const target = event.target;
    const field = target.name;
    return {
        type: UPDATE_MONITORING_PROFILE,
        data: {[field]: target.type === 'checkbox' ? target.checked : target.value}
    };
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any): any {
    return {type: SET_ERROR, errors};
}

export const SET_COMPANY = 'SET_COMPANY';
export function setCompany(company: any): any {
    return {type: SET_COMPANY, company};
}

export const SET_MONITORING_LIST = 'SET_MONITORING_LIST';
export function setMonitoringList(data: any): any {
    return {type: SET_MONITORING_LIST, data};
}

export const SET_USER_COMPANY_MONITORING_LIST = 'SET_USER_COMPANY_MONITORING_LIST';
export function setUserCompanyMonitoringList(data: any): any {
    return {type: SET_USER_COMPANY_MONITORING_LIST, data};
}

export const QUERY_MONITORING = 'QUERY_MONITORING';
export function queryMonitoring(): any {
    return {type: QUERY_MONITORING};
}

export const SELECT_MONITORING_PROFILE = 'SELECT_MONITORING_PROFILE';
export function selectMonitoringProfile(id: any): any {
    return {type: SELECT_MONITORING_PROFILE, id};
}

export const SET_MONITORING_COMPANIES = 'SET_MONITORING_COMPANIES';
export function setMonitoringCompanies(data: any): any {
    return {type: SET_MONITORING_COMPANIES, data};
}

export const SET_SCHEDULE_MODE = 'SET_SCHEDULE_MODE';
export function toggleScheduleMode(): any {
    return {type: SET_SCHEDULE_MODE};
}

export function postMonitoringProfile(userProfile: any, notifyMsg: any): any {
    return function (dispatch: any, getState: any) {

        const p = userProfile || monitoringProfileToEdit(getState());
        const url = `/monitoring/${p._id ? p._id : 'new'}`;

        return server.post(url, p)
            .then(function(item) {
                if (p._id) {
                    notify.success(notifyMsg || gettext('Monitoring Profile updated successfully'));
                } else {
                    notify.success(gettext('Monitoring Profile created successfully'));
                    if (!userProfile) {
                        dispatch(updateMonitoringProfile({
                            target: {
                                name: '_id',
                                value: item._id,
                            }
                        }));

                        if (item.users) {
                            dispatch(updateMonitoringProfile({
                                target: {
                                    name: 'users',
                                    value: item.users,
                                }
                            }));
                        }
                    }
                }
                dispatch(cancelEdit());
                dispatch(fetchMonitoring(get(userProfile, 'company')));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));

    };
}

export function fetchMonitoring(userCompany?: any): any {
    return function (dispatch: any, getState: any) {
        dispatch(queryMonitoring());
        const companyFilter = userCompany || company(getState());
        const filter = get(companyFilter, 'length', 0) > 0 ? '&where={"company":"' + companyFilter + '"}' : '';

        return server.get(`/monitoring/all?q=${filter}`)
            .then((data: any) => {
                if (!userCompany) {
                    dispatch(setMonitoringList(data));
                } else {
                    dispatch(setUserCompanyMonitoringList(data));
                }

                if (!scheduleMode(getState())) {
                    return;
                }

                return dispatch(fetchMonitoringCompanies());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function fetchMonitoringCompanies(): any {
    return function (dispatch: any) {
        return server.get('/monitoring/schedule_companies')
            .then((data: any) => {
                dispatch(setMonitoringCompanies(data));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function saveMonitoringProfileUsers(users: any): any {
    return function (dispatch: any, getState: any) {
        const p = monitoringProfileToEdit(getState());
        return server.post(`/monitoring/${p._id}/users`, {users})
            .then(() => {
                notify.success(gettext('Monitoring Profile users updated successfully'));
                dispatch(fetchMonitoring());
                dispatch(cancelEdit());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function saveMonitoringProfileSchedule(): any {
    return function (dispatch: any, getState: any) {
        const p = monitoringProfileToEdit(getState());
        if (!p._id) {
            notify.error(gettext('Please create the monitoring profile first.'));
        }

        return server.post(`/monitoring/${p._id}/schedule`, {schedule: p.schedule})
            .then(() => {
                notify.success(gettext('Monitoring Profile schedule updated successfully'));
                dispatch(fetchMonitoring());
                dispatch(cancelEdit());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function deleteMonitoringProfile(): any {
    return function (dispatch: any, getState: any) {

        const p = monitoringProfileToEdit(getState());
        const url = `/monitoring/${p._id}`;

        return server.del(url)
            .then(() => {
                notify.success(gettext('Monitoring Profile deleted successfully'));
                dispatch(fetchMonitoring());
                dispatch(cancelEdit());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}
