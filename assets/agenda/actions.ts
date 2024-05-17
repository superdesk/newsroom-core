import {get, isEmpty, includes, cloneDeep} from 'lodash';
import moment from 'moment';

import {
    IRestApiResponse,
    IAgendaItem,
    IAgendaListGroup,
    IAgendaState,
    AgendaThunkAction, ISearchState,
} from 'interfaces';
import server from 'server';
import analytics from 'analytics';
import {
    gettext,
    notify,
    updateRouteParams,
    getTimezoneOffset,
    recordAction,
    copyTextToClipboard,
    errorHandler,
} from 'utils';
import {noNavigationSelected, getNavigationUrlParam} from 'search/utils';

import {markItemAsRead, toggleFeaturedOnlyParam} from 'local-store';
import {renderModal, setSavedItemsCount} from 'actions';
import {
    getDateInputDate,
    getMomentDate,
    groupItems,
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
import {ILocation} from 'interfaces/agenda';

const WATCH_URL = '/agenda_watch';
const WATCH_COVERAGE_URL = '/agenda_coverage_watch';

export const SET_STATE = 'SET_STATE';
export function setState(state: any) {
    return {type: SET_STATE, state};
}

export const SET_ITEMS = 'SET_ITEMS';
export function setItems(items: any) {
    return {type: SET_ITEMS, items};
}

export const SET_ACTIVE = 'SET_ACTIVE';
export function setActive(item: any) {
    return {type: SET_ACTIVE, item};
}


export const PREVIEW_ITEM = 'PREVIEW_ITEM';
export function preview(item: any, group?: any, plan?: any) {
    return {type: PREVIEW_ITEM, item, group, plan};
}

export function previewAndCopy(item: any) {
    return (dispatch: any) => {
        dispatch(copyPreviewContents(item));
    };
}

export function previewItem(item?: any, group?: any, plan?: any) {
    return (dispatch: any, getState: any) => {
        dispatch(fetchWireItemsForAgenda(item));
        markItemAsRead(item, getState());
        dispatch(preview(item, group, plan));
        recordAction(item, 'preview', getState().context, getState());
    };
}

export function fetchWireItemsForAgenda(item?: IAgendaItem) {
    return (dispatch: any) => {
        const wireIds = (item?.coverages || [])
            .filter((coverage) => coverage.coverage_type === 'text')
            .map((coverage) => (
                (coverage.deliveries || [])
                    .map((delivery) => delivery.delivery_id || '')
                    .filter((wireId) => wireId.length > 0)
            ))
            .flat();

        if (wireIds.length > 0){
            return server.get(`/wire/items/${wireIds.join(',')}`)
                .then((items: any) => {
                    dispatch(agendaWireItems(items));
                    return Promise.resolve(items);
                })
                .catch((error: any) => errorHandler(error, dispatch));
        }
    };
}

export const AGENDA_WIRE_ITEMS = 'AGENDA_WIRE_ITEMS';
export function agendaWireItems(items: any) {
    return {type: AGENDA_WIRE_ITEMS, items};
}

export const OPEN_ITEM = 'OPEN_ITEM';
export function openItemDetails(item: any, group?: any, plan?: any) {
    return {type: OPEN_ITEM, item, group, plan};
}

export function requestCoverage(item: any, message: any) {
    return () => {
        const url = '/agenda/request_coverage';
        const data: any = {item: item._id, message};
        return server.post(url, data)
            .then(() => notify.success(gettext('Your inquiry has been sent successfully')))
            .catch((arg: any) => {
                errorHandler(arg);
            });
    };
}

export function openItem(item: any, group: any, plan: any) {
    return (dispatch: any, getState: any) => {
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
export function recieveItems(data: IRestApiResponse<IAgendaItem>) {
    return {type: RECIEVE_ITEMS, data};
}

export const SET_LIST_GROUPS_AND_ITEMS = 'SET_LIST_GROUPS_AND_ITEMS';
function setListGroupsAndItems(groupItems: Array<IAgendaListGroup>) {
    return {type: SET_LIST_GROUPS_AND_ITEMS, data: groupItems};
}

export const ADD_ITEMS_TO_LIST_GROUPS = 'ADD_ITEMS_TO_LIST_GROUPS';
function addItemsToListGroups(groupItems: Array<IAgendaListGroup>) {
    return {type: ADD_ITEMS_TO_LIST_GROUPS, data: groupItems};
}

export const TOGGLE_HIDDEN_GROUP_ITEMS = 'TOGGLE_HIDDEN_GROUP_ITEMS';
export function toggleHiddenGroupItems(dateString: string) {
    return {type: TOGGLE_HIDDEN_GROUP_ITEMS, data: dateString};
}

export const RECIEVE_ITEM = 'RECIEVE_ITEM';
export function recieveItem(data: any) {
    return {type: RECIEVE_ITEM, data};
}

export const INIT_DATA = 'INIT_DATA';
export function initData(agendaData: any, readData: any, activeDate: any, featuredOnly: any) {
    return {type: INIT_DATA, agendaData, readData, activeDate, featuredOnly};
}

export const SELECT_DATE = 'SELECT_DATE';
export function selectDate(dateString: any, grouping: any) {
    return {type: SELECT_DATE, dateString, grouping};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any) {
    return {type: SET_ERROR, errors};
}

export function printItem(item: any) {
    return (dispatch: any, getState: any) => {
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
export function copyPreviewContents(item: any) {
    return (dispatch: any, getState: any) => {
        const state = getState();

        if (!state.user) {
            return;
        }

        (server as any).post(`/wire/${item._id}/copy?type=${state.context}`)
            .then((response: any) => {
                dispatch(setCopyItem(item._id));
                copyTextToClipboard(response.data, item);
            })
            .catch(errorHandler);
    };
}

function search(state: IAgendaState, fetchFrom: number): Promise<IRestApiResponse<IAgendaItem>> {
    const {
        itemType,
        searchParams,
        featured,
        fromDate,
        toDate,
    } = getAgendaSearchParamsFromState(state);

    const params: any = {
        q: searchParams.query,
        bookmarks: state.bookmarks && state.user,
        navigation: getNavigationUrlParam(searchParams.navigation, true, false),
        filter: !isEmpty(searchParams.filter) && encodeURIComponent(JSON.stringify(searchParams.filter)),
        from: fetchFrom,
        date_from: fromDate,
        date_to: toDate,
        timezone_offset: getTimezoneOffset(),
        featured: featured,
        itemType: itemType,
        advanced: !searchParams.advanced ? null : encodeURIComponent(JSON.stringify(searchParams.advanced)),
        es_highlight: !searchParams.query && !searchParams.advanced ? null : 1,
    };

    const queryString = Object.keys(params)
        .filter((key: any) => params[key])
        .map((key: any) => [key, params[key]].join('='))
        .join('&');

    return server.get(`/agenda/search?${queryString}&tick=${Date.now().toString()}`);
}

export const LOADING_AGGREGATIONS = 'LOADING_AGGREGATIONS';
function loadingAggregations() {
    return {type: LOADING_AGGREGATIONS};
}
/**
 * Fetch items for current query
 */
export function fetchItems(): AgendaThunkAction {
    return (dispatch, getState) => {
        const start = Date.now();
        dispatch(queryItems());
        dispatch(loadingAggregations());
        return search(getState(), 0)
            .then((data) => {
                dispatch(recieveItems(data));
                return dispatch(setListGroupsAndLoadHiddenItems(data._items, false));
            })
            .then(() => {
                analytics.timingComplete('search', Date.now() - start);
            })
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}

interface AgendaSearchParams {
    itemType: IAgendaState['agenda']['itemType'];
    searchParams: any;
    featured: boolean;
    fromDate?: string;
    toDate?: string;
}

function getAgendaSearchParamsFromState(state: IAgendaState): AgendaSearchParams {
    const itemTypeFilter = state.agenda.itemType;
    const eventsOnlyFilter = !state.bookmarks && itemTypeFilter === 'events';
    const searchParams: any = searchParamsSelector(state);
    const createdFilter: ISearchState['createdFilter'] = searchParams.created || {};
    const currentMoment = moment();
    const featuredFilter = noNavigationSelected(searchParams.navigation) &&
        !state.bookmarks &&
        !eventsOnlyFilter &&
        state.agenda.featuredOnly === true;
    let fromDate: string | undefined;

    if (featuredFilter) {
        fromDate = getMomentDate(state.agenda.activeDate).set({
            hour: currentMoment.hour(),
            minute: currentMoment.minute()
        }).format('DD/MM/YYYY HH:mm'); // Server expects specific date/time format for FeaturedStories param
    } else {
        const agendaDate = getDateInputDate(state.agenda.activeDate);

        fromDate = (
            createdFilter.from == null &&
            createdFilter.to == null &&
            state.bookmarks !== true
        ) ? agendaDate : createdFilter.from;
    }

    return {
        itemType: itemTypeFilter,
        searchParams: searchParams,
        featured: featuredFilter,
        fromDate: fromDate,
        toDate: createdFilter.from?.startsWith('now/') ?
            createdFilter.from :
            createdFilter.to,
    };
}

function setListGroupsAndLoadHiddenItems(items: Array<IAgendaItem>, next?: boolean): AgendaThunkAction {
    return (dispatch, getState) => {
        // If there are groups shown, then load the hidden items for those groups
        const state = getState();
        const {activeGrouping, featuredOnly} = state.agenda;
        const {fromDate, toDate} = getAgendaSearchParamsFromState(state);
        let minDate: moment.Moment | undefined;
        let maxDate: moment.Moment | undefined;

        if (state.bookmarks !== true) {
            if (toDate != null && fromDate?.startsWith('now/') != true) {
                maxDate = moment(toDate);
            }
            if (fromDate?.startsWith('now/')) {
                if (fromDate === 'now/w') {
                    minDate = moment().startOf('week');
                    maxDate = minDate.clone().add(1, 'week').subtract(1, 'day');
                } else if (fromDate === 'now/M') {
                    minDate = moment().startOf('month');
                    maxDate = minDate.clone().add(1, 'month').subtract(1, 'day');
                } else {
                    minDate = moment().startOf('day');
                    maxDate = minDate.clone();
                }
            } else {
                minDate = moment(fromDate);
            }
            minDate.set({'h': 0, 'm': 0, 's': 0});

            if (maxDate != null) {
                maxDate.set({'h': 23, 'm': 59, 's': 59});
            }
        }

        const groups = groupItems(items, minDate, maxDate, activeGrouping, featuredOnly);

        next === true ?
            dispatch(addItemsToListGroups(groups)) :
            dispatch(setListGroupsAndItems(groups));

        return;
    };
}

export function fetchItem(id: any) {
    return (dispatch: any) => {
        return server.get(`/agenda/${id}?format=json`)
            .then((data: any) => dispatch(recieveItem(data)))
            .catch(errorHandler);
    };
}

export const WATCH_EVENTS = 'WATCH_EVENTS';
export function watchEvents(ids: any) {
    return (dispatch: any, getState: any) => {
        server.post(WATCH_URL, {items: ids})
            .then(() => {
                dispatch({type: WATCH_EVENTS, items: ids});
                notify.success(gettext('Started watching items successfully.'));
                analytics.multiItemEvent('watch', ids.map((_id: any) => getState().itemsById[_id]));
            });
    };
}

export const STOP_WATCHING_EVENTS = 'STOP_WATCHING_EVENTS';
export function stopWatchingEvents(items: any) {
    return (dispatch: any, getState: any) => {
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
export function shareItems(items: any) {
    return (dispatch: any, getState: any) => {
        const user = getState().user;
        const company = getState().company;
        return server.get(`/companies/${company}/users`)
            .then((users: any) => users.filter((u: any) => u._id !== user))
            .then((users: any) => dispatch(renderModal('shareItem', {items, users})))
            .catch(errorHandler);
    };
}

export const BOOKMARK_ITEMS = 'BOOKMARK_ITEMS';
export function setBookmarkItems(items: any) {
    return {type: BOOKMARK_ITEMS, items};
}

export const REMOVE_BOOKMARK = 'REMOVE_BOOKMARK';
export function removeBookmarkItems(items: any) {
    return {type: REMOVE_BOOKMARK, items};
}

export function bookmarkItems(items: any) {
    return (dispatch: any, getState: any) =>
        server.post('/agenda_bookmark', {items})
            .then(() => {
                if (items.length > 1) {
                    notify.success(gettext('Items were bookmarked successfully.'));
                } else {
                    notify.success(gettext('Item was bookmarked successfully.'));
                }
            })
            .then(() => {
                analytics.multiItemEvent('bookmark', items.map((_id: any) => getState().itemsById[_id]));
            })
            .then(() => dispatch(setBookmarkItems(items)))
            .catch(errorHandler);
}

export function removeBookmarks(items: any) {
    return (dispatch: any, getState: any) =>
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
export function toggleSelected(item: any) {
    return {type: TOGGLE_SELECTED, item};
}

export const SHARE_ITEMS = 'SHARE_ITEMS';
export function setShareItems(items: any) {
    return {type: SHARE_ITEMS, items};
}

export const DOWNLOAD_ITEMS = 'DOWNLOAD_ITEMS';
export function setDownloadItems(items: any) {
    return {type: DOWNLOAD_ITEMS, items};
}

export const COPY_ITEMS = 'COPY_ITEMS';
export function setCopyItem(item: any) {
    return {type: COPY_ITEMS, items: [item]};
}

export const PRINT_ITEMS = 'PRINT_ITEMS';
export function setPrintItem(item: any) {
    return {type: PRINT_ITEMS, items: [item]};
}


/**
 * Download items - display modal to pick a format
 *
 * @param {Array} items
 */
export function downloadItems(items: any) {
    return renderModal('downloadItems', {items});
}

/**
 * Personalize Home - display modal to personalize home
 *
 * @param {Array} items
 */
export function personalizeHome(items?: any) {
    return renderModal('personalizeHome', {items});
}

export const REMOVE_NEW_ITEMS = 'REMOVE_NEW_ITEMS';
export function removeNewItems(data: any) {
    return {type: REMOVE_NEW_ITEMS, data};
}

/**
 * Handle server push notification
 *
 * @param {Object} data
 */
export function pushNotification(push: any) {
    return (dispatch: any, getState: any) => {
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

export function reloadMyTopics(reloadTopic: any = false) {
    return function(dispatch: any) {
        return loadMyTopics()
            .then((data: any) => {
                const agendaTopics = data.filter((topic: any) => topic.topic_type === 'agenda');
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
export function setAndUpdateNewItems(data: any) {
    return function(dispatch: any, getState: any) {
        const item = data.item || {};
        const state = getState();

        if (item.type !== 'agenda') {

            // Check if the item is used in the preview or opened agenda item
            // If yes, make it available to the preview
            if (item !== 'text' || (!state.previewItem && !state.openItem)) {
                return Promise.resolve();
            }

            const agendaItem = state.openItem ? state.openItem : state.itemsById[state.previewItem];
            if (!agendaItem || get(agendaItem, 'coverages.length', 0) === 0) {
                return Promise.resolve();
            }

            const coveragesToCheck = (agendaItem.coverages || []).map((c: any) => c.coverage_id);

            if (coveragesToCheck.includes(item.coverage_id)) {
                dispatch(fetchWireItemsForAgenda(agendaItem));
            }

            return Promise.resolve();
        }

        const {itemsById} = state;
        const prevItem = itemsById[item['_id']];

        // If coverage is updated in the item fetch all items and reintilized group listing.
        if (prevItem && prevItem.coverages?.length !== item?.coverages?.length) {
            dispatch(fetchItems());
        } else {
            dispatch(updateItem(item));
            if (item.item_type === 'event' && item.planning_items && item.planning_items.length > 0) {
                item.planning_items.forEach((plan: IAgendaItem) => {
                    dispatch(fetchItem(plan._id));}
                );
            }
        }
        // Do not use 'killed' items for new-item notifications
        if (item.state === 'killed') {
            return Promise.resolve();
        }

        dispatch({type: SET_NEW_ITEM, data: item});
        return Promise.resolve();
    };
}

export const UPDATE_ITEM = 'UPDATE_ITEM';
export function updateItem(item: any) {
    return {type: UPDATE_ITEM, item: item};
}

export function toggleDropdownFilter(key: any, val: any, single = true) {
    return (dispatch: any) => {
        dispatch(setActive(null));
        dispatch(preview(null));

        if (key === 'itemType') {
            dispatch(setItemTypeFilter(val));
        } else if (key === 'location') {
            dispatch(toggleLocationFilter(val));
        } else {
            dispatch(toggleFilter(key, val, single));
        }

        dispatch(fetchItems());
    };
}

function toggleLocationFilter(location: ILocation) {
    return (dispatch: any, getState: any) => {
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
export function recieveNextItems(data: IRestApiResponse<IAgendaItem>, setFetchFrom: boolean) {
    return {type: RECIEVE_NEXT_ITEMS, data: {...data, setFetchFrom: setFetchFrom}};
}

const MAX_ITEMS = 1000; // server limit
export function fetchMoreItems(): AgendaThunkAction {
    return (dispatch, getState) => {
        const state = getState();
        const limit = Math.min(MAX_ITEMS, state.totalItems);

        if (state.isLoading || state.items.length >= limit) {
            return Promise.reject();
        }

        dispatch(startLoading());
        return search(getState(), state.fetchFrom)
            .then((data) => {
                dispatch(recieveNextItems(data, true));
                return dispatch(setListGroupsAndLoadHiddenItems(data._items, true));
            })
            .catch(errorHandler);
    };
}

/**
 * Set state on app init using url params
 *
 * @param {URLSearchParams} params
 */
export function initParams(params: any): any {
    if (params.get('filter') || params.get('created')) {
        clearAgendaDropdownFilters();
    }

    return (dispatch: any, getState: any) => {
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
export function loadMyAgendaTopic(topicId: any) {
    return (dispatch: any, getState: any) => {
        // Set featured query option to false when using navigations
        if (get(getState(), 'agenda.featuredOnly')) {
            dispatch({type: TOGGLE_FEATURED_FILTER});
        }

        dispatch(loadMyTopic(topicId));
        return dispatch(fetchItems());
    };
}

export const TOGGLE_FEATURED_FILTER = 'TOGGLE_FEATURED_FILTER';
export function toggleFeaturedFilter(fetch: any = true) {
    return (dispatch: any) => {
        toggleFeaturedOnlyParam();
        dispatch({type: TOGGLE_FEATURED_FILTER});
        if (!fetch) {
            return Promise.resolve;
        }

        return dispatch(fetchItems());
    };
}

export const SET_ITEM_TYPE_FILTER = 'SET_ITEM_TYPE_FILTER';
export function setItemTypeFilter(value: any) {
    return {type: SET_ITEM_TYPE_FILTER, value};
}

export const WATCH_COVERAGE = 'WATCH_COVERAGE';
export function watchCoverage(coverage: any, item: any) {
    return (dispatch: any) => {
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
            }, (error: any) => { errorHandler(error, dispatch);});
    };
}

export const STOP_WATCHING_COVERAGE = 'STOP_WATCHING_COVERAGE';
export function stopWatchingCoverage(coverage: any, item: any) {
    return (dispatch: any, getState: any) => {
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
            }, (error: any) => { errorHandler(error, dispatch);});
    };
}
