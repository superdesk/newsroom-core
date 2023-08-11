import {gettext} from '../utils';
import {get} from 'lodash';

export const userTypes = [
    {value: 'administrator', text: gettext('Administrator'), show_acc_mgr: false},
    {value: 'internal', text: gettext('Internal'), show_acc_mgr: false},
    {value: 'public', text: gettext('Public'), show_acc_mgr: true},
    {value: 'account_management', text: gettext('Account Management'), show_acc_mgr: false},
    {value: 'company_admin', text: gettext('Company Admin'), show_acc_mgr: true},
];

export function getUserLabel(code: any) {
    return (userTypes.find(c => c.value === code) || {}).text;
}

export function userTypeReadOnly(user: any, currentUser: any) {
    if (get(currentUser, 'user_type') === 'account_management' &&
            (userTypes.find(c => c.value === get(user, 'user_type')) || {}).show_acc_mgr === false)
        return true;
    return false;
}

export function getUserTypes(user: any) {
    if (isUserAdmin(user) || isUserCompanyAdmin(user)) {
        return userTypes;
    }
    return userTypes.filter((opt: any) => (get(opt, 'show_acc_mgr') === true));
}

export function isUserAdmin(user: any) {
    return get(user, 'user_type') === 'administrator';
}

export function isUserCompanyAdmin(user: any) {
    return get(user, 'user_type') === 'company_admin';
}

export function canUserManageTopics(user: any) {
    return isUserAdmin(user) || get(user, 'manage_company_topics') === true;
}

export function getLocaleInputOptions() {
    return (window.locales || [])
        .filter((locale: any) => locale.locale !== window.locale) // this will be default value
        .map((locale: any) => ({value: locale.locale, text: locale.name}));
}

export function getDefaultLocale() {
    return window.locales.find((locale: any) => locale.locale === window.locale).name;
}

export function canUserUpdateTopic(user: any, topic: any) {
    return !topic.is_global || (topic.is_global && user.manage_company_topics === true);
}

export function cleanUserEntityBeforePatch(data: Dictionary<any>) {
    const fieldsToRemove = ['products', 'sections', 'signup_details', '_created', '_updated', '_etag'];

    fieldsToRemove.forEach((x) => {
        delete data[x];
    });

    return data;
}
