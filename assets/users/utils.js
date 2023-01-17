import {gettext} from '../utils';
import {get} from 'lodash';

export const userTypes = [
    {value: 'administrator', text: gettext('Administrator'), show_acc_mgr: false},
    {value: 'internal', text: gettext('Internal'), show_acc_mgr: true},
    {value: 'public', text: gettext('Public'), show_acc_mgr: true},
    {value: 'account_management', text: gettext('Account Management'), show_acc_mgr: false},
    {value: 'company_admin', text: gettext('Company Admin'), show_acc_mgr: false},
];

export function getUserLabel(code) {
    return (userTypes.find(c => c.value === code) || {}).text;
}

export function userTypeReadOnly(user, currentUser) {
    if (get(currentUser, 'user_type') === 'account_management' &&
            (userTypes.find(c => c.value === get(user, 'user_type')) || {}).show_acc_mgr === false)
        return true;
    return false;
}

export function getUserTypes(user) {
    if (isUserAdmin(user)) {
        return userTypes;
    }
    return userTypes.filter((opt) => (get(opt, 'show_acc_mgr') === true));
}

export function isUserAdmin(user) {
    return get(user, 'user_type') === 'administrator';
}

export function canUserManageTopics(user) {
    return isUserAdmin(user) || get(user, 'manage_company_topics') === true;
}

export function getLocaleInputOptions() {
    return (window.locales || [])
        .filter((locale) => locale.locale !== window.locale) // this will be default value
        .map((locale) => ({value: locale.locale, text: locale.name}));
}

export function getDefaultLocale() {
    return window.locales.find((locale) => locale.locale === window.locale).name;
}
