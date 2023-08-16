import {get, cloneDeep, assign, pickBy} from 'lodash';

import server from 'server';
import analytics from 'analytics';

import {getTimezoneOffset, errorHandler, notify, gettext, updateRouteParams, toggleValue} from 'utils';
import {getNavigationUrlParam, getSearchParams} from './utils';
import {getLocations, getMapSource} from 'maps/utils';

import {closeModal} from 'actions';
import {setShareItems} from 'wire/actions';
import {createOrUpdateTopic} from 'user-profile/actions';

import {multiSelectTopicsConfigSelector} from 'ui/selectors';
import {
    searchFilterSelector,
    searchNavigationSelector,
    searchCreatedSelector,
    searchTopicIdSelector,
    activeTopicSelector,
    searchParamsSelector,
} from './selectors';

import {context} from 'selectors';

export const SET_QUERY = 'SET_QUERY';
export function setQuery(query: any) {
    return function(dispatch: any, getState: any) {
        query && analytics.event('search', query);
        dispatch(setSearchQuery(query));
        updateRouteParams(
            {q: query},
            getState()
        );
    };
}

export const SET_SORT_QUERY = 'SET_SORT_QUERY';
export function setSortQuery(sortQuery: string) {
    return function(dispatch: any, getState: any) {
        dispatch(setSearchSortQuery(sortQuery));
        updateRouteParams(
            {sort: sortQuery},
            getState()
        );
    };
}

export const TOGGLE_TOPIC = 'TOGGLE_TOPIC';
export function toggleTopic(topic: any) {
    return {type: TOGGLE_TOPIC, topic};
}

export const ADD_TOPIC = 'ADD_TOPIC';
export function addTopic(topic: any) {
    return {type: ADD_TOPIC, topic};
}

export const SET_NEW_ITEM_BY_TOPIC = 'SET_NEW_ITEM_BY_TOPIC';
export function setNewItemByTopic(data: any) {
    return {type: SET_NEW_ITEM_BY_TOPIC, data};
}

export function loadMyTopics() {
    return server.get('/topics/my_topics');
}

export const SET_TOPICS = 'SET_TOPICS';
export function setTopics(topics: any) {
    return {type: SET_TOPICS, topics};
}

export const TOGGLE_NAVIGATION = 'TOGGLE_NAVIGATION';
export function toggleNavigation(navigation?: any, disableSameNavigationDeselect?: any): any {
    return (dispatch: any, getState: any) => {
        const state = getState();
        const currentNavigation = searchNavigationSelector(state);
        let newNavigation = [...currentNavigation];
        const navigationId = get(navigation, '_id') || navigation;

        if (!navigationId) {
            // If no id has been provided, then we select all topics
            newNavigation = [];
        } else if (multiSelectTopicsConfigSelector(state)) {
            // If multi selecting topics is enabled for this section
            if (currentNavigation.includes(navigationId)) {
                // The navigation is already selected, so deselect it
                newNavigation = newNavigation.filter(
                    (navId: any) => navId !== navigationId
                );
            } else {
                // The navigation is not selected, so select it now
                newNavigation.push(navigationId);
            }
        } else {
            // If multi selecting topics is disabled for this section
            if (get(currentNavigation, '[0]') === navigationId && !disableSameNavigationDeselect) {
                // The navigation is already selected, so deselect it
                newNavigation = [];
            } else {
                // The navigation is not selected, so select it now
                newNavigation = [navigationId];
            }
        }

        dispatch(setSearchNavigationIds(newNavigation));
        updateRouteParams(
            {
                topic: null,
                q: null,
                created: null,
                navigation: getNavigationUrlParam(newNavigation, false),
                filter: null,
                product: null,
                advanced: null,
            },
            state
        );
    };
}

export const TOGGLE_FILTER = 'TOGGLE_FILTER';
export function toggleFilter(key: any, value: any, single?: any) {
    return function (dispatch: any, getState: any) {
        const state = getState();
        const currentFilters = cloneDeep(searchFilterSelector(state));

        // the `value` can be an Array
        const values = Array.isArray(value) ? value : [value];

        for (const _value of values) {
            currentFilters[key] = toggleValue(currentFilters[key], _value);
            if (!_value || !currentFilters[key] || currentFilters[key].length === 0) {
                delete currentFilters[key];
            } else if (single) {
                currentFilters[key] = currentFilters[key].filter(
                    (val: any) => val === _value
                );
            }
        }

        dispatch(setSearchFilters(currentFilters));
        updateRouteParams(
            {filter: currentFilters},
            state,
            false
        );
    };
}

export const SET_CREATED_FILTER = 'SET_CREATED_FILTER';
export function setCreatedFilter(filter: any) {
    return function(dispatch: any, getState: any) {
        const state = getState();

        // Combine the current created filter with the one provided
        // (removing keys where the value is null)
        const created = pickBy(
            assign(
                cloneDeep(searchCreatedSelector(state)),
                filter
            )
        );

        dispatch(setSearchCreated(created));
        updateRouteParams(
            {created},
            state,
            false
        );
    };
}

export const RESET_FILTER = 'RESET_FILTER';
export function resetFilter(filter?: any) {
    return function(dispatch: any, getState: any) {
        updateRouteParams({
            filter: null,
            created: null,
        }, getState());
        dispatch({type: RESET_FILTER, filter});
    };
}

export const SET_VIEW = 'SET_VIEW';
export function setView(view: any) {
    localStorage.setItem('view', view);
    return {type: SET_VIEW, view};
}

/**
 * Start a follow topic action
 *
 * @param {Object} searchParams
 */
export function saveMyTopic(searchParams: any) {
    const type = get(searchParams, 'topic_type') || 'wire';

    const menu = type === 'agenda' ?
        'events' :
        'topics';

    if (!get(searchParams, 'label')) {
        searchParams.label = get(searchParams, 'query.length', 0) > 0 ?
            searchParams.query :
            '';
    }

    createOrUpdateTopic(menu, searchParams, true);
}

export function followStory(item: any, type: any) {
    const slugline = get(item, 'slugline');

    saveMyTopic({
        label: slugline,
        query: `slugline:"${slugline}"`,
        topic_type: type,
    });
}

/**
 * Toggle navigation by id
 *
 * @param {String} navigationId
 */
export function toggleNavigationById(navigationId: any): any {
    return (dispatch: any, getState: any) => {
        const navigation = (get(getState().search, 'navigations') || []).find((nav: any) => navigationId === nav._id);
        if (navigation) {
            dispatch(toggleNavigation(navigation));
        }
    };
}

/**
 * Toggle navigation by ids
 *
 * @param {Array<String>} navigationIds
 */
export function toggleNavigationByIds(navigationIds: any) {
    return (dispatch: any, getState: any) => {
        const navigations = (get(getState().search, 'navigations') || []);

        toggleNavigation();
        navigations
            .filter((nav: any) => navigationIds.includes(nav._id))
            .forEach((nav: any) => dispatch(toggleNavigation(nav)));
    };
}

export function submitFollowTopic(data: any) {
    return (dispatch: any, getState: any) => {
        const user = getState().user;
        const userId = get(user, '_id') || user;

        const url = `/users/${userId}/topics`;
        data.timezone_offset = getTimezoneOffset();
        return server.post(url, data)
            .then((updates: any) => {
                const topic = Object.assign(data, updates);

                dispatch(addTopic(topic));
                dispatch(closeModal());
                return topic;
            })
            .catch(errorHandler);
    };
}

/**
 * Submit share item form and close modal if that works
 *
 * @param {Object} data
 */
export function submitShareItem(data: any) {
    return (dispatch: any, getState: any) => {
        const userContext = context(getState());
        const type = userContext || data.items[0].topic_type;
        data.maps = [];
        let url = 'wire_share';
        if (userContext === 'monitoring') {
            url = 'monitoring/share';
            data.monitoring_profile = get(getState(), 'search.activeNavigation[0]');
        }

        if (type === 'agenda') {
            data.items.map((_id: any) => data.maps.push(getMapSource(getLocations(getState().itemsById[_id]), 2)));
        }
        return server.post(`/${url}?type=${type}`, data)
            .then(() => {
                dispatch(closeModal());
                dispatch(setShareItems(data.items));
                if (data.items.length > 1) {
                    notify.success(gettext('Items were shared successfully.'));
                } else {
                    notify.success(gettext('Item was shared successfully.'));
                }
            })
            .then(() => analytics.multiItemEvent('share', data.items.map((_id: any) => getState().itemsById[_id])))
            .catch(errorHandler);
    };
}

export function deselectMyTopic() {
    return function(dispatch: any, getState: any) {
        const state = getState();
        const currentParams = searchParamsSelector(state);

        dispatch(setSearchTopicId(null));
        dispatch(setParams(currentParams));
        updateRouteParams({
            topic: null,
            q: currentParams.query,
            created: currentParams.created,
            filter: currentParams.filter,
            navigation: currentParams.navigation,
            product: currentParams.product,
            advanced: currentParams.advanced,
        }, getState());
    };
}

export function loadMyTopic(topicId: any): any {
    return (dispatch: any, getState: any) => {
        const state = getState();
        const currentTopicId = searchTopicIdSelector(state);
        const nextTopicId = topicId === currentTopicId ? null : topicId;

        dispatch(resetSearchParams());
        dispatch(setSearchTopicId(nextTopicId));
        updateRouteParams({
            topic: nextTopicId,
            q: null,
            created: null,
            navigation: null,
            filter: null,
            advanced: null,
        }, state);

        dispatch(updateSearchParams());
    };
}

export function updateSearchParams() {
    return function(dispatch: any, getState: any) {
        dispatch(setParams(
            activeTopicSelector(getState())
        ));
    };
}

export function updateFilterStateAndURL(activeFilter: any, createdFilter: any) {
    return function(dispatch: any, getState: any) {
        const state = getState();
        dispatch(setSearchFilters(activeFilter));
        dispatch(setSearchCreated(createdFilter));
        updateRouteParams(
            {filter: activeFilter, created: createdFilter},
            state,
            false
        );
    };
}

export const SET_SEARCH_TOPIC_ID = 'SET_SEARCH_TOPIC_ID';
export function setSearchTopicId(topicId: any) {
    return {type: SET_SEARCH_TOPIC_ID, payload: topicId};
}

export const SET_SEARCH_NAVIGATION_IDS = 'SET_SEARCH_NAVIGATION_IDS';
export function setSearchNavigationIds(navIds: any) {
    return {type: SET_SEARCH_NAVIGATION_IDS, payload: navIds};
}

export const SET_SEARCH_QUERY = 'SET_SEARCH_QUERY';
export function setSearchQuery(query: any) {
    if (query) {
        analytics.event('search', query);
    }

    return {type: SET_SEARCH_QUERY, payload: query};
}

export const SET_SEARCH_SORT_QUERY = 'SET_SEARCH_SORT_QUERY';
export function setSearchSortQuery(sortQuery: any) {
    return {type: SET_SEARCH_SORT_QUERY, payload: sortQuery};
}

export const SET_SEARCH_FILTERS = 'SET_SEARCH_FILTERS';
export function setSearchFilters(filters: any) {
    return {type: SET_SEARCH_FILTERS, payload: filters};
}

export const SET_SEARCH_CREATED = 'SET_SEARCH_CREATED';
export function setSearchCreated(created: any) {
    return {type: SET_SEARCH_CREATED, payload: created};
}

export const SET_SEARCH_PRODUCT = 'SET_SEARCH_PRODUCT';
export function setSearchProduct(productId: any) {
    return {type: SET_SEARCH_PRODUCT, payload: productId};
}

export const RESET_SEARCH_PARAMS = 'RESET_SEARCH_PARAMS';
export function resetSearchParams() {
    return {type: RESET_SEARCH_PARAMS};
}

export function resetSearchParamsAndUpdateURL() {
    return function(dispatch: any, getState: any) {
        dispatch(resetSearchParams());
        updateRouteParams(
            {
                topic: null,
                q: null,
                created: null,
                navigation: null,
                filter: null,
                product: null,
                advanced: null,
            },
            getState()
        );
    };
}

export const TOGGLE_ADVANCED_SEARCH_FIELD = 'TOGGLE_ADVANCED_SEARCH_FIELD';
export function toggleAdvancedSearchField(field: any) {
    return function(dispatch: any, getState: any) {
        const selected = getState().search.advanced.fields;

        if (selected.length === 1 && selected.includes(field)) {
            return; // at least 1 fields must be selected
        }

        dispatch({
            type: TOGGLE_ADVANCED_SEARCH_FIELD,
            payload: field,
        });

        const state = getState();

        updateRouteParams(
            {advanced: state.search.advanced},
            state
        );
    };
}

export const SET_ADVANCED_SEARCH_KEYWORDS = 'SET_ADVANCED_SEARCH_KEYWORDS';
export function setAdvancedSearchKeywords(field: any, keywords: any) {
    return function(dispatch: any, getState: any) {
        dispatch({
            type: SET_ADVANCED_SEARCH_KEYWORDS,
            payload: {
                field: field,
                keywords: keywords,
            }
        });
        const state = getState();

        updateRouteParams(
            {advanced: state.search.advanced},
            state
        );
    };
}

export const CLEAR_ADVANCED_SEARCH_PARAMS = 'CLEAR_ADVANCED_SEARCH_PARAMS';
export function clearAdvancedSearchParams() {
    return function(dispatch: any, getState: any) {
        dispatch({type: CLEAR_ADVANCED_SEARCH_PARAMS});
        updateRouteParams(
            {advanced: null},
            getState()
        );
    };
}

export const SET_ADVANCED_SEARCH_PARAMS = 'SET_ADVANCED_SEARCH_PARAMS';
function setAdvancedSearchParams(params: any) {
    return {
        type: SET_ADVANCED_SEARCH_PARAMS,
        payload: params,
    };
}
export function setParams(params: any) {
    return function(dispatch: any) {
        if (get(params, 'created')) {
            dispatch(setSearchCreated(params.created));
        }

        if (get(params, 'query')) {
            dispatch(setSearchQuery(params.query));
        }

        if (get(params, 'navigation.length', 0) > 0) {
            dispatch(setSearchNavigationIds(params.navigation));
        }

        if (get(params, 'filter')) {
            dispatch(setSearchFilters(params.filter));
        }

        if (get(params, 'product')) {
            dispatch(setSearchProduct(params.product));
        }

        if (get(params, 'advanced')) {
            dispatch(setAdvancedSearchParams(params.advanced));
        }
    };
}

/**
 * Set state on app init using url params
 *
 * @param {URLSearchParams} params
 */
export function initParams(params: any) {
    return (dispatch: any, getState: any) => {
        const custom: any = {
            query: params.get('q'),
            created: params.get('created') ? JSON.parse(params.get('created')) : null,
            navigation: params.get('navigation') ? JSON.parse(params.get('navigation')) : null,
            filter: params.get('filter') ? JSON.parse(params.get('filter')) : null,
            product: params.get('product'),
            advanced: params.get('advanced') ? JSON.parse(params.get('advanced')) : null,
        };
        let topic: any = {};

        if (params.get('topic')) {
            dispatch(setSearchTopicId(params.get('topic')));
            topic = activeTopicSelector(getState());
        }

        dispatch(
            setParams(
                getSearchParams(custom, topic)
            )
        );
    };
}

export function subscribeToTopic(topic: any) {
    (server as any).post(`/topics/${topic._id}/subscribe`)
        .then(() => {
            notify.success(gettext('Topic subscribed successfully'));
        })
        .catch(errorHandler);
}

export function unsubscribeToTopic(topic: any) {
    (server as any).del(`/topics/${topic._id}/subscribe`)
        .then(() => {
            notify.success(gettext('Topic unsubscribed successfully'));
        })
        .catch(errorHandler);
}
