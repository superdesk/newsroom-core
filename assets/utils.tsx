import React from 'react';
import server from 'server';
import analytics from 'analytics';
import {get, isInteger, keyBy, isEmpty, cloneDeep, throttle, memoize} from 'lodash';
import {Provider} from 'react-redux';
import {createStore as _createStore, applyMiddleware, compose, Store, Middleware} from 'redux';
import {createLogger} from 'redux-logger';
import thunk, {ThunkAction} from 'redux-thunk';
import alertify from 'alertifyjs';
import moment from 'moment-timezone';

import {IArticle, IClientConfig, IUser} from 'interfaces';

/*
 * Import and load all locales that will be used in moment.js
 * This should match the LANGUAGES defined in settings.py
 *
 * 'en' comes by default
 */
// TODO: Improve how we load Moment locales, based on server config
import 'moment/locale/fr-ca';
import 'moment/locale/fi';

moment.locale(getLocale());
window.moment = moment;

// CP don't want 2e 3e etc., only 1er
if (getLocale() === 'fr_CA') {
    moment.updateLocale('fr-ca', {
        ordinal: (number: any) => number + (number === 1 ? 'er' : ''),
        weekdays: 'Dimanche_Lundi_Mardi_Mercredi_Jeudi_Vendredi_Samedi'.split('_'),
    });
}

export const now = moment(); // to enable mocking in tests

function getLocaleFormat(formatType: any, defaultFormat?: any) {
    const formats = getConfig('locale_formats', {});
    const locale = getLocale();

    if (formats[locale] && formats[locale][formatType]) {
        return formats[locale][formatType];
    }

    const defaultLanguage = getConfig('default_language', 'en');

    if (formats[defaultLanguage] && formats[defaultLanguage][formatType]) {
        return formats[defaultLanguage][formatType];
    }

    return defaultFormat || 'DD-MM-YYYY';
}

const getTimeFormat = () => getLocaleFormat('TIME_FORMAT');
const getDateFormat = () => getLocaleFormat('DATE_FORMAT');
const getCoverageDateTimeFormat = () =>
    getLocaleFormat('COVERAGE_DATE_TIME_FORMAT');
const getCoverageDateFormat = () => getLocaleFormat('COVERAGE_DATE_FORMAT');

export const TIME_FORMAT = getTimeFormat();
export const DATE_FORMAT = getDateFormat();
export const COVERAGE_DATE_TIME_FORMAT = getCoverageDateTimeFormat();
export const COVERAGE_DATE_FORMAT = getCoverageDateFormat();
export const DATETIME_FORMAT = getLocaleFormat('DATETIME_FORMAT', `${TIME_FORMAT} ${DATE_FORMAT}`);
export const AGENDA_DATE_FORMAT_SHORT = getLocaleFormat('AGENDA_DATE_FORMAT_SHORT', 'dddd, MMMM D');
export const AGENDA_DATE_PICKER_FORMAT_SHORT = getLocaleFormat('AGENDA_DATE_FORMAT_SHORT', 'dddd, MMMM D');
export const AGENDA_DATE_FORMAT_LONG = getLocaleFormat('AGENDA_DATE_FORMAT_LONG', 'dddd, MMMM D, YYYY');

export const SERVER_DATETIME_FORMAT = 'YYYY-MM-DDTHH:mm:ss+0000';
export const DAY_IN_MINUTES = 24 * 60 - 1;
export const LIST_ANIMATIONS = getConfig('list_animations', true);
export const DISPLAY_NEWS_ONLY = getConfig('display_news_only', true);
export const DISPLAY_AGENDA_FEATURED_STORIES_ONLY = getConfig('display_agenda_featured_stories_only', true);
export const DISPLAY_ALL_VERSIONS_TOGGLE = getConfig('display_all_versions_toggle', true);
export const DEFAULT_TIMEZONE = getConfig('default_timezone', 'Australia/Sydney');
export const KEYCODES = {
    ENTER: 13,
    DOWN: 40,
};

export function assertNever(x: any): never {
    throw new Error('Unexpected object: ' + x);
}

/**
 * Create redux store with default middleware
 *
 * @param {func} reducer
 * @param {String} name
 * @return {Store}
 */
export function createStore<State = any>(reducer: any, name: any = 'default'): Store<State, any> {
    // https://redux.js.org/api-reference/compose
    let _compose = compose;
    const middlewares: Array<Middleware> = [
        thunk
    ];

    if (getConfig('debug')) {
        // activate logs actions for non production instances.
        // (this should always be the last middleware)
        middlewares.push(
            createLogger({
                duration: true,
                collapsed: true,
                timestamp: false,
                titleFormatter: (action: any, time: any, took: any) => (
                    // Adds the name of the store to the console logs
                    // derived based on the defaultTitleFormatter from redux-logger
                    // https://github.com/LogRocket/redux-logger/blob/master/src/core.js#L25
                    (action && action.type) ?
                        `${name} - action ${String(action.type)} (in ${took.toFixed(2)} ms)` :
                        `${name} - action (in ${took.toFixed(2)} ms)`
                ),
            })
        );
        // activate redux devtools for non production instances,
        // if it's available in the browser
        // https://github.com/zalmoxisus/redux-devtools-extension
        if (window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__) {
            _compose = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__;
        }
    }

    return _createStore<State, any, any, any>(reducer, _compose(applyMiddleware(...middlewares)));
}

/**
 * Noop for now, but it's better to use it from beginning.
 *
 * It handles interpolation:
 *
 * gettext('Hello {{ name }}', {name: 'John'});
 *
 * @param {String} text
 * @param {Object} params
 * @return {String}
 */
export function gettext(text: string, params?: {[key: string]: any}): string {
    let translated = get(window.translations, text, text);

    if (params) {
        Object.keys(params).forEach((param: string) => {
            const paramRegexp = new RegExp('{{ ?' + param + ' ?}}', 'g');
            translated = translated.replace(paramRegexp, params[param] != null ? params[param] : '');
        });
    }

    return translated;
}

/**
 * Returns query string query for a given product
 *
 * @param {Object} product
 * @return {string}
 */
export function getProductQuery(product: any) {
    let q = product.sd_product_id ? `products.code:${product.sd_product_id}` : '';
    q += product.query ? product.sd_product_id ? ` OR (${product.query})` : product.query : '';
    return q;
}

/**
 * Parse given date string and return Date instance
 *
 * @param {String} dateString
 * @param {Boolean} ignoreTimezone - avoid converting time to different timezone, will output the date as it is
 * @return {Date}
 */
export function parseDate(dateString: any, ignoreTimezone: any = false) {
    const parsed = ignoreTimezone ? moment.utc(dateString) : moment(dateString);

    parsed.locale(getLocale());

    return parsed;
}

/**
 * Parse the given date string and return moment instance in the timezone provided
 * If no timezone is provided, then it will default to the browser's timezone
 * @param {String} dateString - The datetime string to convert
 * @param {String} timezone - The name of the timezone region, i.e. Australia/Sydney
 * @returns {moment}
 */
export function parseDateInTimezone(dateString: any, timezone: any = null) {
    return moment.tz(dateString, timezone || moment.tz.guess());
}

/**
 * Return date formatted for lists
 *
 * @param {String} dateString
 * @param {String} timeForToday - if true show only time if date is today
 * @return {String}
 */
export function shortDate(dateString: any, timeForToday: any = true) {
    const parsed = parseDate(dateString);
    return parsed.format(timeForToday === true && isToday(parsed) ? TIME_FORMAT : DATE_FORMAT);
}

/**
 * Return date formatted for date inputs
 *
 * @param {String} dateString
 * @return {String}
 */
export function getDateInputDate(dateString: any) {
    if (dateString) {
        const parsed = parseDate(dateString.substring(0, 10));
        return parsed.format('YYYY-MM-DD');
    }

    return '';
}

/**
 * Return locale date
 *
 * @param {String} dateString
 * @return {String}
 */
export function getLocaleDate(dateString: any) {
    return parseDate(dateString).format(DATETIME_FORMAT);
}

/**
 * Test if given day is today
 *
 * @param {Date} date
 * @return {Boolean}
 */
export function isToday(date: any) {
    const parsed = typeof date === 'string' ? parseDate(date) : date;
    return parsed.format('YYYY-MM-DD') === now.format('YYYY-MM-DD');
}


/**
 * Test if given day is in the past
 * If no timezone is provided, then it will default to the browser's timezone
 *
 * @param {String} dateString - The datetime string to check
 * @param {String} timezone - The name of the timezone region, i.e. Australia/Sydney
 * @return {Boolean}
 */
export function isInPast(dateString: any, timezone?: any) {
    if(!dateString) {
        return false;
    }

    return parseDateInTimezone(dateString, timezone).isSameOrBefore(
        now.tz(timezone || moment.tz.guess()),
        'day'
    );
}

/**
 * Return full date representation
 *
 * @param {String} dateString
 * @return {String}
 */
export function fullDate(dateString: any) {
    return parseDate(dateString).format(DATETIME_FORMAT);
}

/**
 * Format time of a date
 *
 * @param {String} dateString
 * @return {String}
 */
export function formatTime(dateString: any) {
    return parseDate(dateString).format(TIME_FORMAT);
}

/**
 * Format date of a date (without time)
 *
 * @param {String} dateString
 * @return {String}
 */
export function formatDate(dateString: any) {
    return parseDate(dateString).format(DATE_FORMAT);
}

/**
 * Format date with time
 *
 * @param {String} dateString
 * @return {String}
 */
export function formatDatetime(dateString: any) {
    return fullDate(dateString);
}

/**
 * Parse the given date string, setting the time to 23:59:59 (i.e. end of the day).
 * Ensures that the datetime is for the end of the day in the provided timezone
 * If no timezone is provided, then it will default to the browser's timezone
 * @param {String} dateString - The date string to convert (in the format 'YYYY-MM-DD')
 * @param {String} timezone - The name of the timezone region, i.e. Australia/Sydney
 * @returns {moment}
 */
export function getEndOfDayFromDate(dateString: any, timezone: any = null) {
    return parseDateInTimezone(dateString + 'T23:59:59', timezone);
}

/**
 * Parse the given datetime string and timezone and converts it to utc
 * If no timezone is provided, then it will default to the browser's timezone
 * @param {String} datetime - The datetime string
 * @param {String} timezone - The name of the timezone region, i.e. Australia/Sydney
 * @returns {moment}
 */
export function convertUtcToTimezone(datetime: any, timezone: any) {
    return parseDateInTimezone(datetime, 'utc')
        .tz(timezone);
}

/**
 * Format week of a date (without time)
 *
 * @param {String} dateString
 * @return {String}
 */
export function formatWeek(dateString: any) {
    const startDate = parseDate(dateString).isoWeekday(1);
    const endDate = parseDate(dateString).isoWeekday(7);
    return `${startDate.format(DATE_FORMAT)} - ${endDate.format(DATE_FORMAT)}`;
}

/**
 * Format month of a date (without time)
 *
 * @param {String} dateString
 * @return {String}
 */
export function formatMonth(dateString: any) {
    return parseDate(dateString).format('MMMM');
}

/**
 * Wrapper for alertifyjs
 */
export const notify = {
    success: (message: any) => alertify.success(message),
    error: (message: any) => alertify.error(message),
    warning: (message: any) => alertify.warning(message),
};

/**
 * Get text from html
 *
 * @param {string} html
 * @return {string}
 */
export function getTextFromHtml(html: any) {
    const raw_html = (html || '').trim();

    if (raw_html.length === 0) {
        return '';
    } else if (raw_html[0] !== '<') {
        // No need to convert if the string doesn't start with a tag
        return raw_html;
    }

    const div = document.createElement('div');
    div.innerHTML = formatHTML(raw_html);
    const tree = (document as any).createTreeWalker(div, NodeFilter.SHOW_TEXT, null, false); // ie requires all params
    const text: Array<any> = [];
    while (tree.nextNode()) {
        text.push(tree.currentNode.textContent);
        if (tree.currentNode.nextSibling) {
            switch(tree.currentNode.nextSibling.nodeName) {
            case 'BR':
            case 'HR':
                text.push('\n');
            }

            continue;
        }

        switch (tree.currentNode.parentNode.nodeName) {
        case 'P':
        case 'LI':
        case 'H1':
        case 'H2':
        case 'H3':
        case 'H4':
        case 'H5':
        case 'DIV':
        case 'TABLE':
        case 'BLOCKQUOTE':
            text.push('\n');
        }
    }

    return text.join('');
}

/**
 * Get word count for given item
 *
 * @param {Object} item
 * @return {number}
 */
export function wordCount(item: any) {
    if (isInteger(item.wordcount)) {
        return item.wordcount;
    }

    if (!item.body_html) {
        return 0;
    }

    const text = getTextFromHtml(item.body_html);
    return text.split(' ').filter((x: any) => x.trim()).length || 0;
}

/**
 * Get character count for given item
 *
 * @param {Object} item
 * @return {number}
 */
export function characterCount(item: any) {

    if (isInteger(item.charcount)) {
        return item.charcount;
    }

    if (!item.body_html) {
        return 0;
    }

    const text = getTextFromHtml(item.body_html);

    // Ignore the last line break
    return text.length - 1 ;
}

/**
 * Toggle value within array
 *
 * returns a new array so can be used with setState
 *
 * @param {Array} items
 * @param {mixed} value
 * @return {Array}
 */
export function toggleValue(items: any, value: any) {
    if (!items) {
        return [value];
    }

    const without = items.filter((x: any) => value !== x);
    return without.length === items.length ? without.concat([value]) : without;
}


export function updateRouteParams(updates: any, state: any, deleteEmpty: any = true) {
    const params = new URLSearchParams(window.location.search);

    Object.keys(updates).forEach((key: any) => {
        let updatedValue = updates[key];
        if (!deleteEmpty || !isEmpty(updatedValue) || typeof updatedValue === 'boolean') {
            if (typeof updatedValue === 'object') {
                updatedValue = JSON.stringify(updatedValue);
            }
            params.set(key, updatedValue);
        } else {
            params.delete(key);
        }
    });

    const stateClone = cloneDeep(state);
    stateClone.items = [];
    stateClone.itemsById = {};
    (history as any).pushState(stateClone, null, `?${params.toString()}`);
}

const SHIFT_OUT_REGEXP = new RegExp(String.fromCharCode(14), 'g');

/**
 * Replace some white characters in html
 *
 * @param {String} html
 * @return {String}
 */
export function formatHTML(html: any) {
    return html.replace(SHIFT_OUT_REGEXP, html.indexOf('<pre>') === -1 ? '<br>' : '\n');
}

export const SET_ERROR_MESSAGE = 'SET_ERROR_MESSAGE';
function setErrorMessage(message: any) {
    return {
        type: SET_ERROR_MESSAGE,
        message
    };
}

/**
 * Generic error handler for http requests
 * @param error
 * @param dispatch
 * @param setError
 */
export function errorHandler(error: {errorData: any} | Response, dispatch?: any, setError?: any) {
    if ('errorData' in error) {
        if (setError) {
            dispatch(setError(error.errorData));
        }
    } else {
        if (error.status === 403) {
            dispatch(setErrorMessage(gettext(
                'There is no product associated with your user. Please reach out to your Company Admin',
            )));
        } else if (error.status === 412) {
            notify.warning(gettext('Resource was updated in the meantime, please refresh.'));
        } else {
            notify.error(error.statusText || gettext('Failed to process request!'));
        }
    }
}

/**
 * Get config value
 *
 * @param {String} key
 * @param {Mixed} defaultValue
 * @return {Mixed}
 */
export function getConfig(key: any, defaultValue?: any) {
    const clientConfig = window && window.newsroom && window.newsroom.client_config || {};

    if (Object.keys(clientConfig).length === 0) {
        console.warn('Client config is not yet available for key', key);
    }

    return get(clientConfig, key, defaultValue);
}

export function getLocale() {
    const defaultLanguage = getConfig('default_language', 'en');
    const locale = get(window, 'locale', defaultLanguage);

    return locale;
}

export function getTimezoneOffset() {
    return now.utcOffset() ? now.utcOffset() * -1 : 0; // it's oposite to Date.getTimezoneOffset
}

export function isTouchDevice() {
    return 'ontouchstart' in window        // works on most browsers
    || navigator.maxTouchPoints > 0;       // works on IE10/11 and Surface
}

export function isMobilePhone() {
    return isTouchDevice() && screen.width < 768;
}

/**
 * Checks if wire context
 * @returns {boolean}
 */
export function isWireContext() {
    return window.location.pathname.includes('/wire');
}

export const getInitData = (data: any) => {
    const initData = data || {};
    return {
        ...initData,
        userSections: keyBy(get(window.profileData, 'userSections', {}), '_id')
    };
};

export const isDisplayed = (field: any, config: any, defaultValue = true) => get(config, `${field}.displayed`, defaultValue);

const getNow = throttle(moment, 500);

/**
 * Test if item is embargoed, if not returns null, otherwise returns its embargo time
 * @param {String} embargoed
 * @return {Moment}
 */
export function getEmbargo(item: any) {
    if (!item.embargoed) {
        return null;
    }

    const now = getNow();
    const parsed = moment(item.embargoed);

    return parsed.isAfter(now) ? parsed : null;
}

export function getItemFromArray(value: any, items: Array<any> = [], field: any = '_id') {
    return items.find((i: any) => i[field] === value);
}

export function upperCaseFirstCharacter(text: any) {
    return (text && text.toLowerCase().replace(/\b\w/g, (l: any) => l.toUpperCase()));
}

export function postHistoryAction(item: any, action: any, section: any = 'wire') {
    server.post('/history/new', {
        item: item,
        action: action,
        section: section
    }).catch((error: any) => errorHandler(error));
}

export function recordAction(item: any, action: any = 'open', section: any = 'wire', state: any = null) {
    if (item) {
        analytics.itemEvent(action, item);
        analytics.itemView(item, section);
        postHistoryAction(item, action, section);

        if (action === 'preview') {
            updateRouteParams({}, {
                ...state,
                previewItem: get(item, '_id')
            });
        }
    }
}

export function closeItemOnMobile(dispatch: any, state: any, openItemDetails: any, previewItem: any) {
    if (isMobilePhone()) {
        dispatch(openItemDetails(null));
        dispatch(previewItem(null));
    }
}

/**
 * Get the slugline appended by the takekey if one is defined
 * @param {Object} item - The wire item to get the slugline from
 * @param {boolean} withTakeKey - If true, appends the takekey to the response
 * @returns {String}
 */
export function getSlugline(item: IArticle, withTakeKey: any = false): string {
    if (!item || !item.slugline) {
        return '';
    }

    let slugline = item.slugline.trim();
    const takeKey = ` | ${item.anpa_take_key}`;

    if (withTakeKey && item.anpa_take_key && !slugline.endsWith(takeKey)) {
        slugline += takeKey;
    }

    return slugline;
}

/**
 * Factory for filter function to check if action is enabled
 */
export function isActionEnabled(configKey: any) {
    const config = getConfig(configKey, {});
    return (action: any) => config[action.id] == null || config[action.id];
}

export const getPlainTextMemoized = memoize((html: any) => getTextFromHtml(html));

export function shouldShowListShortcutActionIcons(listConfig: any, isExtended: any) {
    const showActionIconsConfig = listConfig.show_list_action_icons || {
        large: true,
        compact: true,
        mobile: false,
    };

    return isMobilePhone() ?
        showActionIconsConfig.mobile : (
            isExtended ?
                showActionIconsConfig.large :
                showActionIconsConfig.compact
        );
}

export function getCreatedSearchParamLabel(created: any) {
    if (created.to) {
        if (created.from) {
            return {
                from: formatDate(created.from),
                to: formatDate(created.to),
            };
        } else {
            return {
                to: formatDate(created.to),
            };
        }
    } else if (created.from) {
        if (created.from === 'now/d') {
            return {relative: gettext('Today')};
        } else if (created.from === 'now/w') {
            return {relative: gettext('This week')};
        } else if (created.from === 'now/M') {
            return {relative: gettext('This month')};
        } else {
            return {from: formatDate(created.from)};
        }
    }

    return {};
}

export function copyTextToClipboard(text: any, item: any) {
    navigator.clipboard.writeText(text).then(
        () => {
            notify.success(gettext('Item copied successfully.'));
            item && analytics.itemEvent('copy', item);
        },
        () => {
            notify.error(gettext('Sorry, Copy is not supported.'));
        }
    );
}

export function getScheduledNotificationConfig(): IClientConfig['scheduled_notifications'] {
    return getConfig('scheduled_notifications', {default_times: [
        '07:00',
        '15:00',
        '19:00',
    ]});
}

export function getSubscriptionTimesString(user: IUser): string {
    const schedule = user.notification_schedule || {
        timezone: DEFAULT_TIMEZONE,
        times: getScheduledNotificationConfig().default_times,
    };
    const now = moment.tz(schedule.timezone);
    const timezoneAbbreviation = now.zoneAbbr();
    const timeStrings = [];

    for (const time of schedule.times) {
        const time_parts = time.split(':');

        now.hours(parseInt(time_parts[0], 10))
            .minutes(parseInt(time_parts[1], 10));

        timeStrings.push(formatTime(now));
    }

    return gettext('Daily @ {{ time1 }}, {{ time2 }} and {{ time3 }} {{ timezone }}', {
        time1: timeStrings[0],
        time2: timeStrings[1],
        time3: timeStrings[2],
        timezone: timezoneAbbreviation,
    });
}
