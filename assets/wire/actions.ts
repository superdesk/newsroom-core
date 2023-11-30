import {get, isEmpty} from 'lodash';

import {IArticle} from 'interfaces';
import server from 'server';
import analytics from 'analytics';

import {
    gettext,
    notify,
    updateRouteParams,
    getTimezoneOffset,
    recordAction,
    errorHandler,
    copyTextToClipboard,
} from 'utils';
import {getNavigationUrlParam} from 'search/utils';

import {searchParamsSelector} from 'search/selectors';
import {context} from 'selectors';

import {markItemAsRead, toggleNewsOnlyParam, toggleSearchAllVersionsParam} from 'local-store';
import {renderModal, closeModal, setSavedItemsCount} from 'actions';

import {
    initParams as initSearchParams,
    setNewItemByTopic,
    loadMyTopics,
    setTopics,
    loadMyTopic,
} from 'search/actions';

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
export function preview(item: any) {
    return {type: PREVIEW_ITEM, item};
}

export function previewAndCopy(item: any) {
    return (dispatch: any) => {
        dispatch(previewItem(item));
        dispatch(copyPreviewContents(item));
    };
}

export function previewItem(item: any) {
    return (dispatch: any, getState: any) => {
        markItemAsRead(item, getState());
        dispatch(preview(item));
        recordAction(item, 'preview', getState().context, getState());
    };
}

export const OPEN_ITEM = 'OPEN_ITEM';
export function openItemDetails(item: any) {
    return {type: OPEN_ITEM, item};
}

export function openItem(item: any) {
    return (dispatch: any, getState: any) => {
        const state = getState();
        markItemAsRead(item, state);
        dispatch(openItemDetails(item));
        updateRouteParams({
            item: item ? item._id : null
        },  {
            ...state,
            openItem: item,
        });
        recordAction(item, 'open', state.context);
    };
}

export function selectCopy(item: any) {
    return () => {
        recordAction(item, 'clipboard');
    };
}

export const QUERY_ITEMS = 'QUERY_ITEMS';
export function queryItems() {
    return {type: QUERY_ITEMS};
}

export const LOADING_AGGREGATIONS = 'LOADING_AGGREGATIONS';
function loadingAggregations() {
    return {type: LOADING_AGGREGATIONS};
}

export const RECIEVE_ITEMS = 'RECIEVE_ITEMS';
export function recieveItems(data: any) {
    return {type: RECIEVE_ITEMS, data};
}

export const RECIEVE_AGGS = 'RECIEVE_AGGS';
function recieveAggs(data: any) {
    return {type: RECIEVE_AGGS, data};
}

export const RECIEVE_ITEM = 'RECIEVE_ITEM';
export function recieveItem(data: any) {
    return {type: RECIEVE_ITEM, data};
}

export const INIT_DATA = 'INIT_DATA';
export function initData(wireData: any, newsOnlyFilterText?: any, readData?: any, newsOnly?: any, searchAllVersions?: any) {
    return {type: INIT_DATA, wireData, newsOnlyFilterText, readData, newsOnly, searchAllVersions};
}

export const TOGGLE_NEWS = 'TOGGLE_NEWS';
export function toggleNews() {
    toggleNewsOnlyParam();
    return {type: TOGGLE_NEWS};
}

export const TOGGLE_SEARCH_ALL_VERSIONS = 'TOGGLE_SEARCH_ALL_VERSIONS';
export function toggleSearchAllVersions() {
    toggleSearchAllVersionsParam();
    return {type: TOGGLE_SEARCH_ALL_VERSIONS};
}

export function removeItems(items: any) {
    if (confirm(gettext('Are you sure you want to permanently remove these item(s)?'))) {
        return server.del('/wire', {items})
            .then(() => {
                if (items.length > 1) {
                    notify.success(gettext('Items were removed successfully'));
                } else {
                    notify.success(gettext('Item was removed successfully'));
                }
            })
            .catch(errorHandler);
    }

    return Promise.resolve();
}

export const WIRE_ITEM_REMOVED = 'WIRE_ITEM_REMOVED';
/**
 * Marks the items as deleted when they're removed from the system
 * @param {Array<String>} ids - List of ids of items that were removed
 */
export function onItemsDeleted(ids: any) {
    return {type: WIRE_ITEM_REMOVED, ids: ids};
}

/**
 * Copy contents of item preview.
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

export function printItem(item: any) {
    return (dispatch: any, getState: any) => {
        const userContext = context(getState());
        let uri = `/${userContext}/${item._id}?print`;
        if (userContext === 'monitoring') {
            const monitoringProfile = get(getState(), 'search.activeNavigation[0]');
            uri = `${uri}=true&monitoring_profile=${monitoringProfile}&type=monitoring`;
        }
        window.open(uri, '_blank');
        item && analytics.itemEvent('print', item);
        if (getState().user) {
            dispatch(setPrintItem(item._id));
        }
    };
}

/**
 * Search server request
 *
 * @param {Object} state
 * @param {bool} next
 * @param {bool} aggs
 * @return {Promise}
 */
export function search(state: any, next?: any, aggs?: any) {
    const searchParams = searchParamsSelector(state);
    const createdFilter = get(searchParams, 'created') || {};
    let created_to = createdFilter.to;

    if (createdFilter.from && createdFilter.from.indexOf('now') >= 0) {
        created_to = createdFilter.from;
    }

    const newsOnly = !!get(state, 'wire.newsOnly');
    const searchAllVersions = !!get(state, 'wire.searchAllVersions');
    const context = get(state, 'context', 'wire');

    const params: any = {
        sort: !searchParams.sortQuery ? null : searchParams.sortQuery,
        q: !searchParams.query ? null : encodeURIComponent(searchParams.query),
        bookmarks: state.bookmarks ? state.user : null,
        navigation: getNavigationUrlParam(searchParams.navigation, true, false),
        filter: !isEmpty(searchParams.filter) ? encodeURIComponent(JSON.stringify(searchParams.filter)) : null,
        from: next ? state.items.length : 0,
        created_from: createdFilter.from,
        created_to,
        timezone_offset: getTimezoneOffset(),
        newsOnly,
        product: searchParams.product,
        es_highlight: !searchParams.query && !searchParams.advanced ? null : 1,
        all_versions: !searchAllVersions ? null : 1,
        prepend_embargoed: !state.bookmarks ? null : 0,
        aggs: aggs === false ? '0' : '1',
        size: aggs === true ? 0 : null,
        tick: Date.now().toString(),
        advanced: !searchParams.advanced ? null : encodeURIComponent(JSON.stringify(searchParams.advanced))
    };


    const queryString = Object.keys(params)
        .filter((key: any) => params[key] != null && params[key].toString() !== '')
        .map((key: any) => `${key}=${params[key]}`)
        .join('&');

    return server.get(`/${context}/search?${queryString}`);
}

/**
 * Fetch items for current query
 */
export function fetchItems(): any {
    return (dispatch: any, getState: any) => {
        const start = Date.now();
        dispatch(queryItems());
        dispatch(loadingAggregations());
        dispatch(previewItem(null));
        const state = getState();
        return Promise.all([
            search(state, false, false)
                .then((data: any) => dispatch(recieveItems(data)))
                .then(() => {
                    analytics.timingComplete('search', Date.now() - start);
                })
                .catch(errorHandler),
            search(state, false, true)
                .then((data) => dispatch(recieveAggs(data))),
        ])
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}


export function fetchItem(id: any) {
    return (dispatch: any, getState: any) => {
        return server.get(`/${context(getState())}/${id}?format=json&context=wire`)
            .then((data: any) => dispatch(recieveItem(data)))
            .catch(errorHandler);
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

export const TOGGLE_SELECTED = 'TOGGLE_SELECTED';
export function toggleSelected(item: any) {
    return {type: TOGGLE_SELECTED, item};
}

export const SELECT_ALL = 'SELECT_ALL';
export function selectAll() {
    return {type: SELECT_ALL};
}

export const SELECT_NONE = 'SELECT_NONE';
export function selectNone() {
    return {type: SELECT_NONE};
}

export const SHARE_ITEMS = 'SHARE_ITEMS';
export function setShareItems(items: any) {
    return {type: SHARE_ITEMS, items};
}

export const DOWNLOAD_ITEMS = 'DOWNLOAD_ITEMS';
export function setDownloadItems(items: any) {
    return {type: DOWNLOAD_ITEMS, items};
}

export const EXPORT_ITEMS = 'EXPORT_ITEMS';
export function setExportItems(items: any) {
    return {type: EXPORT_ITEMS, items};
}

export const COPY_ITEMS = 'COPY_ITEMS';
export function setCopyItem(item: any) {
    return {type: COPY_ITEMS, items: [item]};
}

export const PRINT_ITEMS = 'PRINT_ITEMS';
export function setPrintItem(item: any) {
    return {type: PRINT_ITEMS, items: [item]};
}

export const BOOKMARK_ITEMS = 'BOOKMARK_ITEMS';
export function setBookmarkItems(items: any) {
    return {type: BOOKMARK_ITEMS, items};
}

export const REMOVE_BOOKMARK = 'REMOVE_BOOKMARK';
export function removeBookmarkItems(items: any) {
    return {type: REMOVE_BOOKMARK, items};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any) {
    return {type: SET_ERROR, errors};
}

export function bookmarkItems(items: any) {
    return (dispatch: any, getState: any) =>
        server.post(`/${getState().context}_bookmark`, {items})
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
        server.del(`/${getState().context}_bookmark`, {items})
            .then(() => {
                if (items.length > 1) {
                    notify.success(gettext('Items were removed from bookmarks successfully.'));
                } else {
                    notify.success(gettext('Item was removed from bookmarks successfully.'));
                }
            })
            .then(() => dispatch(removeBookmarkItems(items)))
            .then(() => getState().bookmarks &&  dispatch(fetchItems()))
            .catch(errorHandler);
}

/**
 * Fetch item versions.
 *
 * @param {Object} item
 * @return {Promise}
 */
export function fetchVersions(item: IArticle): Promise<Array<IArticle>> {
    return server.get(`/wire/${item._id}/versions`)
        .then((data: {_items: Array<IArticle>}) => (data._items));
}

/**
 * Download media file
 *
 * @param {string} id
 * @param {string} filename
 */
export function downloadMedia(id: any, filename: any) {
    return () => {
        window.open(`/assets/${id}?filename=${filename}`, '_blank');
        analytics.event('download-media', filename || id);
    };
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
 * Start download - open download view in new window.
 *
 * @param {Array} items
 * @param {String} params
 */
export function submitDownloadItems(items: any, params: any) {
    return (dispatch: any, getState: any) => {
        const {format, secondaryFormat} = params;
        const userContext = context(getState());
        let uri = `/download/${items.join(',')}?format=${format}&type=${userContext}`;
        if (userContext === 'monitoring') {
            const monitoringProfile = get(getState(), 'search.activeNavigation[0]');
            uri = `/monitoring/export/${items.join(',')}?format=${format}&monitoring_profile=${monitoringProfile}`;
            uri = `${uri}&secondary_format=${secondaryFormat}`;
        }
        browserDownload(uri);
        dispatch(setDownloadItems(items));
        dispatch(closeModal());
        analytics.multiItemEvent('download', items.map((_id: any) => getState().itemsById[_id]));
    };
}

function browserDownload(url: any) {
    const link = document.createElement('a');
    link.download = '';
    link.href = url;
    link.click();
}

export const REMOVE_NEW_ITEMS = 'REMOVE_NEW_ITEMS';
export function removeNewItems(data: any) {
    return {type: REMOVE_NEW_ITEMS, data};
}

/**
 * Handle server push notification
 *
 * @param {Object} push
 */
export function pushNotification(push: any): any {
    return (dispatch: any, getState: any) => {
        const user = getState().user;
        const company = getState().company;

        switch (push.event) {
        case 'topic_matches':
            return dispatch(setNewItemByTopic(push.extra));

        case 'new_item':
            return dispatch(setNewItems(push.extra));

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

        case 'items_deleted':
            return dispatch(onItemsDeleted(push.extra.ids));
        }
    };
}

export function reloadMyTopics(reloadTopic: any = false) {
    return function(dispatch: any) {
        return loadMyTopics()
            .then((data: any) => {
                const wireTopics = data.filter((topic: any) => !topic.topic_type || topic.topic_type === 'wire');
                dispatch(setTopics(wireTopics));

                if (reloadTopic) {
                    const params = new URLSearchParams(window.location.search);
                    if (params.get('topic')) {
                        dispatch(loadMyWireTopic(params.get('topic')));
                    }
                }
            })
            .catch(errorHandler);
    };
}

export const SET_NEW_ITEMS = 'SET_NEW_ITEMS';
export function setNewItems(data: any) {
    return function (dispatch: any) {
        if (get(data, '_items.length') <= 0 || get(data, '_items[0].type') !== 'text') {
            return Promise.resolve();
        }

        dispatch({type: SET_NEW_ITEMS, data});
        return Promise.resolve();
    };
}

export function fetchNewItems() {
    return (dispatch: any, getState: any) => search(getState())
        .then((response: any) => dispatch(setNewItems(response)));
}

export function fetchNext(item: IArticle): Promise<IArticle> {
    if (item.nextversion == null) {
        return Promise.reject();
    }

    return server.get(`/wire/${item.nextversion}?format=json`);
}

export const TOGGLE_FILTER = 'TOGGLE_FILTER';
export function toggleFilter(key: any, val: any, single: any) {
    return (dispatch: any) => {
        setTimeout(() => dispatch({type: TOGGLE_FILTER, key, val, single}));
    };
}

export const START_LOADING = 'START_LOADING';
export function startLoading() {
    return {type: START_LOADING};
}

export const RECIEVE_NEXT_ITEMS = 'RECIEVE_NEXT_ITEMS';
export function recieveNextItems(data: any) {
    return {type: RECIEVE_NEXT_ITEMS, data};
}

const MAX_ITEMS = 1000; // server limit
export function fetchMoreItems() {
    return (dispatch: any, getState: any) => {
        const state = getState();
        const limit = Math.min(MAX_ITEMS, state.totalItems);

        if (state.isLoading || state.items.length >= limit) {
            return Promise.reject();
        }

        dispatch(startLoading());
        return search(getState(), true)
            .then((data: any) => dispatch(recieveNextItems(data)))
            .catch(errorHandler);
    };
}

export function loadMyWireTopic(topicId: any) {
    return (dispatch: any) => {
        dispatch(loadMyTopic(topicId));
        return dispatch(fetchItems());
    };
}

/**
 * Set state on app init using url params
 *
 * @param {URLSearchParams} params
 */
export function initParams(params: any): any {
    return (dispatch: any, getState: any) => {
        dispatch(initSearchParams(params));
        if (params.get('item')) {
            dispatch(fetchItem(params.get('item')))
                .then(() => {
                    const item = getState().itemsById[params.get('item')];
                    dispatch(openItem(item));
                });
        }
    };
}

