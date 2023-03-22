import {get, isEmpty, includes, cloneDeep} from 'lodash';
import moment from 'moment';

import server from 'server';
import analytics from 'analytics';
import {
    gettext,
    notify,
    updateRouteParams,
    getTimezoneOffset,
    errorHandler,
    recordAction,
    copyTextToClipboard,
} from 'utils';
import {noNavigationSelected, getNavigationUrlParam} from 'search/utils';

import {markItemAsRead, toggleFeaturedOnlyParam} from 'local-store';
import {renderModal, setSavedItemsCount} from 'actions';
import {
    getDateInputDate,
    getMomentDate,
} from './utils';

import {
    toggleFilter,
    initParams as initSearchParams,
    setNewItemByTopic,
    loadMyTopics,
    setTopics,
    loadMyTopic,
    setSearchFilters,
} from 'search/actions';
import {searchParamsSelector, searchFilterSelector} from 'search/selectors';

import {clearAgendaDropdownFilters} from '../local-store';
import {getLocations, getMapSource} from '../maps/utils';

const WATCH_URL = '/agenda_watch';
const WATCH_COVERAGE_URL = '/agenda_coverage_watch';

export const SET_STATE = 'SET_STATE';
export function setState(state) {
    return {type: SET_STATE, state};
}

export const SET_ITEMS = 'SET_ITEMS';
export function setItems(items) {
    return {type: SET_ITEMS, items};
}

export const SET_ACTIVE = 'SET_ACTIVE';
export function setActive(item) {
    return {type: SET_ACTIVE, item};
}


export const PREVIEW_ITEM = 'PREVIEW_ITEM';
export function preview(item, group, plan) {
    return {type: PREVIEW_ITEM, item, group, plan};
}

export function previewAndCopy(item) {
    return (dispatch) => {
        dispatch(copyPreviewContents(item));
    };
}

export function previewItem(item, group, plan) {
    return (dispatch, getState) => {
        dispatch(fetchWireItemsForAgenda(item));
        markItemAsRead(item, getState());
        dispatch(preview(item, group, plan));
        recordAction(item, 'preview', getState().context, getState());
    };
}

export function fetchWireItemsForAgenda(item) {
    return (dispatch) => {
        let wireIds = [];
        (get(item, 'coverages') || []).forEach((c) => {
            if (c.coverage_type === 'text' && c.delivery_id) {
                wireIds.push(c.delivery_id);
            }
        });

        if (wireIds.length > 0){
            return server.get(`/wire/items/${wireIds.join(',')}`)
                .then((items) => {
                    dispatch(agendaWireItems(items));
                    return Promise.resolve(items);
                })
                .catch((error) => errorHandler(error, dispatch));
        }
    };
}

export const AGENDA_WIRE_ITEMS = 'AGENDA_WIRE_ITEMS';
export function agendaWireItems(items) {
    return {type: AGENDA_WIRE_ITEMS, items};
}

export const OPEN_ITEM = 'OPEN_ITEM';
export function openItemDetails(item, group, plan) {
    return {type: OPEN_ITEM, item, group, plan};
}

export function requestCoverage(item, message) {
    return () => {
        const url = '/agenda/request_coverage';
        const data = {item: item._id, message};
        return server.post(url, data)
            .then(() => notify.success(gettext('Your inquiry has been sent successfully')))
            .catch(errorHandler);
    };
}

export function openItem(item, group, plan) {
    return (dispatch, getState) => {
        const state = getState();
        markItemAsRead(item, state);
        dispatch(fetchWireItemsForAgenda(item));
        dispatch(openItemDetails(item, group, plan));
        updateRouteParams({
            item: item ? item._id : null,
            group: group || null,
            plan: plan || null,
        }, {
            ...state,
            openItem: item,
        });
        recordAction(item, 'open', state.context);
    };
}

export const QUERY_ITEMS = 'QUERY_ITEMS';
export function queryItems() {
    return {type: QUERY_ITEMS};
}

export const RECIEVE_ITEMS = 'RECIEVE_ITEMS';
export function recieveItems(data) {
    return {type: RECIEVE_ITEMS, data};
}

export const RECIEVE_ITEM = 'RECIEVE_ITEM';
export function recieveItem(data) {
    return {type: RECIEVE_ITEM, data};
}

export const INIT_DATA = 'INIT_DATA';
export function initData(agendaData, readData, activeDate, featuredOnly) {
    return {type: INIT_DATA, agendaData, readData, activeDate, featuredOnly};
}

export const SELECT_DATE = 'SELECT_DATE';
export function selectDate(dateString, grouping) {
    return {type: SELECT_DATE, dateString, grouping};
}


export function printItem(item) {
    return (dispatch, getState) => {
        const map = encodeURIComponent(getMapSource(getLocations(item), 2));
        window.open(`/agenda/${item._id}?print&map=${map}`, '_blank');

        item && analytics.itemEvent('print', item);
        if (getState().user) {
            dispatch(setPrintItem(item._id));
        }
    };
}


/**
 * Copy contents of agenda preview.
 *
 * This is an initial version, should be updated with preview markup changes.
 */
export function copyPreviewContents(item) {
    return (dispatch, getState) => {
        const state = getState();

        if (!state.user) {
            return;
        }

        server.post(`/wire/${item._id}/copy?type=${state.context}`)
            .then((response) => {
                dispatch(setCopyItem(item._id));
                copyTextToClipboard(response.data, item);
            })
            .catch(errorHandler);
    };
}

/**
 * Search server request
 *
 * @param {Object} state
 * @param {bool} next
 * @return {Promise}
 */
function search(state, next) {
    const currentMoment = moment();
    const searchParams = searchParamsSelector(state);
    const createdFilter = get(searchParams, 'created') || {};
    const itemTypeFilter = get(state, 'agenda.itemType');
    const eventsOnlyFilter = !state.bookmarks && itemTypeFilter === 'events';

    const featuredFilter = noNavigationSelected(searchParams.navigation) &&
        !state.bookmarks &&
        !eventsOnlyFilter &&
        get(state, 'agenda.featuredOnly');

    let fromDateFilter;

    if (featuredFilter) {
        fromDateFilter = getMomentDate(get(state, 'agenda.activeDate')).set({
            hour: currentMoment.hour(),
            minute: currentMoment.minute()
        }).format('DD/MM/YYYY HH:mm'); // Server expects specific date/time format for FeaturedStories param
    } else {
        const agendaDate = getDateInputDate(get(state, 'agenda.activeDate'));
        fromDateFilter = (
            isEmpty(createdFilter.from) &&
            isEmpty(createdFilter.to) &&
            !(state.bookmarks && state.user)
        ) ? agendaDate : createdFilter.from;
    }

    let dateTo = createdFilter.to;
    if (createdFilter.from && createdFilter.from.indexOf('now') >= 0) {
        dateTo = createdFilter.from;
    }

    const params = {
        q: searchParams.query,
        id: state.queryId,
        bookmarks: state.bookmarks && state.user,
        navigation: getNavigationUrlParam(searchParams.navigation, true, false),
        filter: !isEmpty(searchParams.filter) && encodeURIComponent(JSON.stringify(searchParams.filter)),
        from: next ? state.items.length : 0,
        date_from: fromDateFilter,
        date_to: dateTo,
        timezone_offset: getTimezoneOffset(),
        featured: featuredFilter,
        itemType: itemTypeFilter,
    };

    const queryString = Object.keys(params)
        .filter((key) => params[key])
        .map((key) => [key, params[key]].join('='))
        .join('&');

    return server.get(`/agenda/search?${queryString}&tick=${Date.now().toString()}`);
}

/**
 * Fetch items for current query
 */
export function fetchItems() {
    return (dispatch, getState) => {
        const start = Date.now();
        dispatch(queryItems());
        return search(getState())
            .then((data) => dispatch(recieveItems(data)))
            .then(() => {
                analytics.timingComplete('search', Date.now() - start);
            })
            .catch(errorHandler);
    };
}

export function fetchItem(id) {
    return (dispatch) => {
        return server.get(`/agenda/${id}?format=json`)
            .then((data) => dispatch(recieveItem(data)))
            .catch(errorHandler);
    };
}

export const WATCH_EVENTS = 'WATCH_EVENTS';
export function watchEvents(ids) {
    return (dispatch, getState) => {
        server.post(WATCH_URL, {items: ids})
            .then(() => {
                dispatch({type: WATCH_EVENTS, items: ids});
                notify.success(gettext('Started watching items successfully.'));
                analytics.multiItemEvent('watch', ids.map((_id) => getState().itemsById[_id]));
            });
    };
}

export const STOP_WATCHING_EVENTS = 'STOP_WATCHING_EVENTS';
export function stopWatchingEvents(items) {
    return (dispatch, getState) => {
        server.del(getState().bookmarks ? `${WATCH_URL}?bookmarks=true` : WATCH_URL, {items})
            .then(() => {
                notify.success(gettext('Stopped watching items successfully.'));
                if (getState().bookmarks) {
                    if (includes(items, getState().previewItem)) { // close preview if it's opened
                        dispatch(previewItem());
                    }

                    dispatch(fetchItems()); // item should get removed from the list in bookmarks view
                } else { // in agenda toggle item watched state
                    dispatch({type: STOP_WATCHING_EVENTS, items: items});
                }
            });
    };
}

/**
 * Start share item action - display modal to pick users
 *
 * @return {function}
 */
export function shareItems(items) {
    return (dispatch, getState) => {
        const user = getState().user;
        const company = getState().company;
        return server.get(`/companies/${company}/users`)
            .then((users) => users.filter((u) => u._id !== user))
            .then((users) => dispatch(renderModal('shareItem', {items, users})))
            .catch(errorHandler);
    };
}

export const BOOKMARK_ITEMS = 'BOOKMARK_ITEMS';
export function setBookmarkItems(items) {
    return {type: BOOKMARK_ITEMS, items};
}

export const REMOVE_BOOKMARK = 'REMOVE_BOOKMARK';
export function removeBookmarkItems(items) {
    return {type: REMOVE_BOOKMARK, items};
}

export function bookmarkItems(items) {
    return (dispatch, getState) =>
        server.post('/agenda_bookmark', {items})
            .then(() => {
                if (items.length > 1) {
                    notify.success(gettext('Items were bookmarked successfully.'));
                } else {
                    notify.success(gettext('Item was bookmarked successfully.'));
                }
            })
            .then(() => {
                analytics.multiItemEvent('bookmark', items.map((_id) => getState().itemsById[_id]));
            })
            .then(() => dispatch(setBookmarkItems(items)))
            .catch(errorHandler);
}

export function removeBookmarks(items) {
    return (dispatch, getState) =>
        server.del('/agenda_bookmark', {items})
            .then(() => {
                if (items.length > 1) {
                    notify.success(gettext('Items were removed from bookmarks successfully.'));
                } else {
                    notify.success(gettext('Item was removed from bookmarks successfully.'));
                }
            })
            .then(() => dispatch(removeBookmarkItems(items)))
            .then(() => getState().bookmarks && dispatch(fetchItems()))
            .catch(errorHandler);
}

export const TOGGLE_SELECTED = 'TOGGLE_SELECTED';
export function toggleSelected(item) {
    return {type: TOGGLE_SELECTED, item};
}

export const SHARE_ITEMS = 'SHARE_ITEMS';
export function setShareItems(items) {
    return {type: SHARE_ITEMS, items};
}

export const DOWNLOAD_ITEMS = 'DOWNLOAD_ITEMS';
export function setDownloadItems(items) {
    return {type: DOWNLOAD_ITEMS, items};
}

export const COPY_ITEMS = 'COPY_ITEMS';
export function setCopyItem(item) {
    return {type: COPY_ITEMS, items: [item]};
}

export const PRINT_ITEMS = 'PRINT_ITEMS';
export function setPrintItem(item) {
    return {type: PRINT_ITEMS, items: [item]};
}


/**
 * Download items - display modal to pick a format
 *
 * @param {Array} items
 */
export function downloadItems(items) {
    return renderModal('downloadItems', {items});
}

export const REMOVE_NEW_ITEMS = 'REMOVE_NEW_ITEMS';
export function removeNewItems(data) {
    return {type: REMOVE_NEW_ITEMS, data};
}

/**
 * Handle server push notification
 *
 * @param {Object} data
 */
export function pushNotification(push) {
    return (dispatch, getState) => {
        const user = getState().user;
        const company = getState().company;

        switch (push.event) {
        case 'topic_matches':
            return dispatch(setNewItemByTopic(push.extra));

        case 'new_item':
            return dispatch(setAndUpdateNewItems(push.extra));

        case `topics:${user}`:
            return dispatch(reloadMyTopics());

        case `topics:company-${company}`:
            return dispatch(reloadMyTopics());

        case `topic_created:${user}`:
            return dispatch(reloadMyTopics(true));

        case `topic_created:company-${company}`:
            return dispatch(reloadMyTopics(push.extra && push.extra.user_id === user));

        case `saved_items:${user}`:
            return dispatch(setSavedItemsCount(push.extra.count));
        }
    };
}

export function reloadMyTopics(reloadTopic = false) {
    return function(dispatch) {
        return loadMyTopics()
            .then((data) => {
                const agendaTopics = data.filter((topic) => topic.topic_type === 'agenda');
                dispatch(setTopics(agendaTopics));

                if (reloadTopic) {
                    const params = new URLSearchParams(window.location.search);
                    if (params.get('topic')) {
                        dispatch(loadMyAgendaTopic(params.get('topic')));
                    }
                }
            })
            .catch(errorHandler);
    };
}

export const SET_NEW_ITEM = 'SET_NEW_ITEM';
export function setAndUpdateNewItems(data) {
    return function(dispatch, getState) {
        const item = data.item || {};

        if (item.type !== 'agenda') {
            const state = getState();

            // Check if the item is used in the preview or opened agenda item
            // If yes, make it available to the preview
            if (item !== 'text' || (!state.previewItem && !state.openItem)) {
                return Promise.resolve();
            }

            const agendaItem = state.openItem ? state.openItem : state.itemsById[state.previewItem];
            if (!agendaItem || get(agendaItem, 'coverages.length', 0) === 0) {
                return Promise.resolve();
            }

            const coveragesToCheck = (agendaItem.coverages || []).map((c) => c.coverage_id);

            if (coveragesToCheck.includes(item.coverage_id)) {
                dispatch(fetchWireItemsForAgenda(agendaItem));
            }

            return Promise.resolve();
        }

        dispatch(updateItem(item));

        // Do not use 'killed' items for new-item notifications
        if (item.state === 'killed') {
            return Promise.resolve();
        }

        dispatch({type: SET_NEW_ITEM, data: item});
        return Promise.resolve();
    };
}

export const UPDATE_ITEM = 'UPDATE_ITEM';
export function updateItem(item) {
    return {type: UPDATE_ITEM, item: item};
}

export function toggleDropdownFilter(key, val) {
    return (dispatch) => {
        dispatch(setActive(null));
        dispatch(preview(null));

        if (key === 'itemType') {
            dispatch(setItemTypeFilter(val));
        } else if (key === 'location') {
            dispatch(setLocationFilter(val));
        } else {
            dispatch(toggleFilter(key, val, true));
        }

        dispatch(fetchItems());
    };
}

function setLocationFilter(location) {
    return (dispatch, getState) => {
        const state = getState();
        const currentFilters = cloneDeep(searchFilterSelector(state));
        const currentLocation = get(currentFilters, 'location') || {};

        if (location == null || (currentLocation.type === location.type && currentLocation.name === location.name)) {
            delete currentFilters.location;
        } else {
            currentFilters.location = location;
        }

        dispatch(setSearchFilters(currentFilters));
        updateRouteParams(
            {filter: currentFilters},
            state,
            false
        );
    };
}

export const START_LOADING = 'START_LOADING';
export function startLoading() {
    return {type: START_LOADING};
}

export const RECIEVE_NEXT_ITEMS = 'RECIEVE_NEXT_ITEMS';
export function recieveNextItems(data) {
    return {type: RECIEVE_NEXT_ITEMS, data};
}

const MAX_ITEMS = 1000; // server limit
export function fetchMoreItems() {
    return (dispatch, getState) => {
        const state = getState();
        const limit = Math.min(MAX_ITEMS, state.totalItems);

        if (state.isLoading || state.items.length >= limit) {
            return Promise.reject();
        }

        dispatch(startLoading());
        return search(getState(), true)
            .then((data) => dispatch(recieveNextItems(data)))
            .catch(errorHandler);
    };
}

/**
 * Set state on app init using url params
 *
 * @param {URLSearchParams} params
 */
export function initParams(params) {
    if (params.get('filter') || params.get('created')) {
        clearAgendaDropdownFilters();
    }

    return (dispatch, getState) => {
        const featuredParam = params.get('featured');
        if (featuredParam && featuredParam !== get(getState(), 'agenda.featuredOnly', false).toString()) {
            dispatch(toggleFeaturedFilter(false));
        }

        dispatch(setItemTypeFilter(params.get('itemType', null)));
        dispatch(initSearchParams(params));
        if (params.get('item')) {
            dispatch(fetchItem(params.get('item')))
                .then(() => {
                    const item = getState().itemsById[params.get('item')];

                    dispatch(openItem(item, params.get('group'), params.get('plan')));
                });
        }
    };
}

/**
 * Set query for given topic
 *
 * @param {String} topicId
 * @return {Promise}
 */
export function loadMyAgendaTopic(topicId) {
    return (dispatch, getState) => {
        // Set featured query option to false when using navigations
        if (get(getState(), 'agenda.featuredOnly')) {
            dispatch({type: TOGGLE_FEATURED_FILTER});
        }

        dispatch(loadMyTopic(topicId));
        return dispatch(fetchItems());
    };
}

export const TOGGLE_FEATURED_FILTER = 'TOGGLE_FEATURED_FILTER';
export function toggleFeaturedFilter(fetch = true) {
    return (dispatch) => {
        toggleFeaturedOnlyParam();
        dispatch({type: TOGGLE_FEATURED_FILTER});
        if (!fetch) {
            return Promise.resolve;
        }

        return dispatch(fetchItems());
    };
}

export const SET_ITEM_TYPE_FILTER = 'SET_ITEM_TYPE_FILTER';
export function setItemTypeFilter(value) {
    return {type: SET_ITEM_TYPE_FILTER, value};
}

export const WATCH_COVERAGE = 'WATCH_COVERAGE';
export function watchCoverage(coverage, item) {
    return (dispatch) => {
        server.post(WATCH_COVERAGE_URL, {
            coverage_id: coverage.coverage_id,
            item_id: item._id
        })
            .then(() => {
                dispatch({
                    type: WATCH_COVERAGE,
                    coverage,
                    item
                });
                notify.success(gettext('Started watching coverage successfully.'));
            }, (error) => { errorHandler(error, dispatch);});
    };
}

export const STOP_WATCHING_COVERAGE = 'STOP_WATCHING_COVERAGE';
export function stopWatchingCoverage(coverage, item) {
    return (dispatch, getState) => {
        server.del(WATCH_COVERAGE_URL, {
            coverage_id: coverage.coverage_id,
            item_id: item._id
        })
            .then(() => {
                notify.success(gettext('Stopped watching coverage successfully.'));
                dispatch({
                    type: STOP_WATCHING_COVERAGE,
                    coverage,
                    item
                });

                if (getState().bookmarks) {
                    dispatch(fetchItems()); // item should get removed from the list in bookmarks view
                }
            }, (error) => { errorHandler(error, dispatch);});
    };
}
