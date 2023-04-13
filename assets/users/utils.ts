import {gettext} from '../utils';
import {get} from 'lodash';

export const userTypes = [
    {value: 'administrator', text: gettext('Administrator'), show_acc_mgr: false},
    {value: 'internal', text: gettext('Internal'), show_acc_mgr: true},
    {value: 'public', text: gettext('Public'), show_acc_mgr: true},
    {value: 'account_management', text: gettext('Account Management'), show_acc_mgr: false},
    {value: 'company_admin', text: gettext('Company Admin'), show_acc_mgr: false},
];

export function getUserLabel(code: any): any {
    return (userTypes.find(c => c.value === code) || {}).text;
}

export function userTypeReadOnly(user: any, currentUser: any): any {
    if (get(currentUser, 'user_type') === 'account_management' &&
            (userTypes.find(c => c.value === get(user, 'user_type')) || {}).show_acc_mgr === false)
        return true;
    return false;
}

export function getUserTypes(user: any): any {
    if (isUserAdmin(user)) {
        return userTypes;
    }
    return userTypes.filter((opt) => (get(opt, 'show_acc_mgr') === true));
}

export function isUserAdmin(user: any): any {
    return get(user, 'user_type') === 'administrator';
}

export function isUserCompanyAdmin(user: any): any {
    return get(user, 'user_type') === 'company_admin';
}

export function canUserManageTopics(user: any): any {
    return isUserAdmin(user) || get(user, 'manage_company_topics') === true;
}

export function getLocaleInputOptions(): any {
    return (window.locales || [])
        .filter((locale) => locale.locale !== window.locale) // this will be default value
        .map((locale) => ({value: locale.locale, text: locale.name}));
}

export function getDefaultLocale(): any {
    return window.locales.find((locale) => locale.locale === window.locale).name;
}
