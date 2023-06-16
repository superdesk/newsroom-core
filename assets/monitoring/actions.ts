import {gettext, notify, errorHandler} from 'utils';
import server from 'server';
import {monitoringProfileToEdit, company, scheduleMode} from './selectors';
import {get} from 'lodash';


export const INIT_DATA = 'INIT_DATA';
export function initData(data: any) {
    return {type: INIT_DATA, data};
}

export const SET_COMPANIES = 'SET_COMPANIES';
export function setCompanies(data: any) {
    return {type: SET_COMPANIES, data};
}

export function initViewData(data: any) {
    return function (dispatch) {
        dispatch(setCompanies(data.companies));
    };
}

export const NEW_MONITORING_PROFILE = 'NEW_MONITORING_PROFILE';
export function newMonitoringProfile() {
    return {type: NEW_MONITORING_PROFILE};
}

export const CANCEL_EDIT = 'CANCEL_EDIT';
export function cancelEdit() {
    return {type: CANCEL_EDIT};
}

export const UPDATE_MONITORING_PROFILE = 'UPDATE_MONITORING_PROFILE';
export function updateMonitoringProfile(event: any) {
    const target = event.target;
    const field = target.name;
    return {
        type: UPDATE_MONITORING_PROFILE,
        data: {[field]: target.type === 'checkbox' ? target.checked : target.value}
    };
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any) {
    return {type: SET_ERROR, errors};
}

export const SET_COMPANY = 'SET_COMPANY';
export function setCompany(company: any) {
    return {type: SET_COMPANY, company};
}

export const SET_MONITORING_LIST = 'SET_MONITORING_LIST';
export function setMonitoringList(data: any) {
    return {type: SET_MONITORING_LIST, data};
}

export const SET_USER_COMPANY_MONITORING_LIST = 'SET_USER_COMPANY_MONITORING_LIST';
export function setUserCompanyMonitoringList(data: any) {
    return {type: SET_USER_COMPANY_MONITORING_LIST, data};
}

export const QUERY_MONITORING = 'QUERY_MONITORING';
export function queryMonitoring() {
    return {type: QUERY_MONITORING};
}

export const SELECT_MONITORING_PROFILE = 'SELECT_MONITORING_PROFILE';
export function selectMonitoringProfile(id: any) {
    return {type: SELECT_MONITORING_PROFILE, id};
}

export const SET_MONITORING_COMPANIES = 'SET_MONITORING_COMPANIES';
export function setMonitoringCompanies(data: any) {
    return {type: SET_MONITORING_COMPANIES, data};
}

export const SET_SCHEDULE_MODE = 'SET_SCHEDULE_MODE';
export function toggleScheduleMode() {
    return {type: SET_SCHEDULE_MODE};
}

export function postMonitoringProfile(userProfile: any, notifyMsg: any) {
    return function (dispatch, getState) {

        const p = userProfile || monitoringProfileToEdit(getState());
        const url = `/monitoring/${p._id ? p._id : 'new'}`;

        return server.post(url, p)
            .then(function(item) {
                if (p._id) {
                    notify.success(notifyMsg || gettext('{{monitoring}} Profile updated successfully', window.sectionNames));
                } else {
                    notify.success(gettext('{{monitoring}} Profile created successfully', window.sectionNames));
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

export function fetchMonitoring(userCompany: any) {
    return function (dispatch, getState) {
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

export function fetchMonitoringCompanies() {
    return function (dispatch) {
        return server.get('/monitoring/schedule_companies')
            .then((data: any) => {
                dispatch(setMonitoringCompanies(data));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function saveMonitoringProfileUsers(users: any) {
    return function (dispatch, getState) {
        const p = monitoringProfileToEdit(getState());
        return server.post(`/monitoring/${p._id}/users`, {users})
            .then(() => {
                notify.success(gettext('{{monitoring}} Profile users updated successfully', window.sectionNames));
                dispatch(fetchMonitoring());
                dispatch(cancelEdit());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function saveMonitoringProfileSchedule() {
    return function (dispatch, getState) {
        const p = monitoringProfileToEdit(getState());
        if (!p._id) {
            notify.error(gettext('Please create {{monitoring}} profile first.', window.sectionNames));
        }

        return server.post(`/monitoring/${p._id}/schedule`, {schedule: p.schedule})
            .then(() => {
                notify.success(gettext('{{monitoring}} Profile schedule updated successfully', window.sectionNames));
                dispatch(fetchMonitoring());
                dispatch(cancelEdit());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

export function deleteMonitoringProfile() {
    return function (dispatch, getState) {

        const p = monitoringProfileToEdit(getState());
        const url = `/monitoring/${p._id}`;

        return server.del(url)
            .then(() => {
                notify.success(gettext('{{monitoring}} Profile deleted successfully', window.sectionNames));
                dispatch(fetchMonitoring());
                dispatch(cancelEdit());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}
