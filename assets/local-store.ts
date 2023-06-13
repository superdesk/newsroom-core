import moment from 'moment';
import Store from 'store';
import localStorage from 'store/storages/localStorage';
import operationsPlugin from 'store/plugins/operations';
import expirePlugin from 'store/plugins/expire';

import {get} from 'lodash';
import {getConfig} from './utils';

const READ_ITEMS_STORE = 'read_items';
const NEWS_ONLY_STORE = 'news_only';
const SEARCH_ALL_VERSIONS_STORE = 'search_all_versions';
const FEATURED_ONLY_STORE = 'featured-only';
const FILTER_TAB = 'filter_tab';
const FILTER_PANEL_OPEN = 'filter_open';
const ACTIVE_DATE = 'active_date';
const DROPDOWN_FILTERS = 'dropdown_filters';

const store = Store.createStore([localStorage], [operationsPlugin, expirePlugin]);

/**
 * Get read items
 *
 * @returns {Object}
 */
export function getReadItems() {
    return store.get(READ_ITEMS_STORE);
}

/**
 * Marks the given item as read
 *
 * @param {Object} item
 * @param {Object} state
 */
export function markItemAsRead(item: any, state: any) {
    if (item && item._id) {
        const readItems = get(state, 'readItems', getReadItems()) || {};

        store.assign(READ_ITEMS_STORE, {[item._id]: getMaxVersion(readItems[item._id], item.version || 0)});
    }
}

/**
 * Get news only value
 *
 * @returns {boolean}
 */
export function getNewsOnlyParam() {
    return !!((store.get(NEWS_ONLY_STORE) || {}).value);
}


/**
 * Toggles news only value
 *
 */
export function toggleNewsOnlyParam() {
    store.assign(NEWS_ONLY_STORE, {value: !getNewsOnlyParam()});
}

/**
 * Get search all versions  value
 *
 * @returns {boolean}
 */
export function getSearchAllVersionsParam() {
    return !!((store.get(SEARCH_ALL_VERSIONS_STORE) || {}).value);
}

/**
 * Toggles search all versions value
 *
 */
export function toggleSearchAllVersionsParam() {
    store.assign(SEARCH_ALL_VERSIONS_STORE, {value: !getSearchAllVersionsParam()});
}

/**
 * Get featured stories only value
 *
 * @returns {boolean}
 */
export function getFeaturedOnlyParam() {
    return !!((store.get(FEATURED_ONLY_STORE) || {}).value);
}


/**
 * Featured stories only value
 *
 */
export function toggleFeaturedOnlyParam() {
    store.assign(FEATURED_ONLY_STORE, {value: !getFeaturedOnlyParam()});
}

export function getFilterPanelOpenState(context: any) {
    const defaultValue = get(getConfig('filter_panel_defaults') || {}, `open.${context}`, false);

    return get(store.get(FILTER_PANEL_OPEN), context, defaultValue);
}

export function setFilterPanelOpenState(open: any, context: any) {
    const filterTabs: any = {...store.get(FILTER_PANEL_OPEN) || {}};

    filterTabs[context] = open;
    store.assign(FILTER_PANEL_OPEN, filterTabs);
}

/**
 * Get active filter tab
 *
 * @returns {boolean}
 */
export function getActiveFilterTab(context: any) {
    const defaultValue = get(getConfig('filter_panel_defaults') || {}, `tab.${context}`, 'nav');

    return get(store.get(FILTER_TAB), context, defaultValue);
}

/**
 * Set active filter tab
 *
 */
export function setActiveFilterTab(tab: any, context: any) {
    let filterTabs: any = {...store.get(FILTER_TAB) || {}};
    filterTabs[context] = tab;
    store.assign(FILTER_TAB, filterTabs);
}


/**
 * Returns the greater version
 *
 * @param versionA
 * @param versionB
 * @returns {number}
 */
export function getMaxVersion(versionA: any, versionB: any) {
    return Math.max(parseInt(versionA, 10) || 0, parseInt(versionB, 10) || 0);
}


/**
 * Returns the expiry date: end of the current day
 * @returns {number}
 */
function getExpiryDate() {
    return moment().endOf('day').valueOf();
}


/**
 * Saves active date value until the end of today
 *
 * @param activeDate
 */
export function setActiveDate(activeDate: any) {
    store.set(ACTIVE_DATE, activeDate, getExpiryDate());
}


/**
 * Returns active date value if not expired
 * @returns {number}
 */
export function getActiveDate() {
    store.removeExpiredKeys();
    return store.get(ACTIVE_DATE);
}


/**
 * Saves given filter and its value until the end of today
 *
 * @param filter
 * @param value
 */
export function setAgendaDropdownFilter(filter: any, value: any) {
    const filters = store.get(DROPDOWN_FILTERS) || {};
    filters[filter] = value;
    store.set(DROPDOWN_FILTERS, filters, getExpiryDate());
}


/**
 * Returns filters and values if not expired
 * @returns {object}
 */
export function getAgendaDropdownFilters() {
    store.removeExpiredKeys();
    return store.get(DROPDOWN_FILTERS);
}

/**
 * Clears filters
 * @returns {object}
 */
export function clearAgendaDropdownFilters() {
    store.remove(DROPDOWN_FILTERS);
}
