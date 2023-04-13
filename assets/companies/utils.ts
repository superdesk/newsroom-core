import {gettext} from '../utils';

export const countries = [
    {value: 'au', text: gettext('Australia')},
    {value: 'nz', text: gettext('New Zealand')},
    {value: 'fin', text: gettext('Finland')},
    {value: 'other', text: gettext('Other')},
];

export function getCountryLabel(code: any): any {
    return (countries.find(c => c.value === code) || {}).text;
}

export function isProductEnabled(products: any, productId: any): any {
    return products.findIndex((product) => product._id === productId) !== -1;
}
