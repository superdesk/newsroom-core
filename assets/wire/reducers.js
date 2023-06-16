import {
    RECIEVE_ITEMS,
    INIT_DATA,
    TOGGLE_NEWS,
    TOGGLE_SEARCH_ALL_VERSIONS,
    WIRE_ITEM_REMOVED,
    RECIEVE_AGGS,
    LOADING_AGGREGATIONS,
    SET_ERROR,
    SET_ERROR_MESSAGE,
} from './actions';

import {get, cloneDeep} from 'lodash';

import {defaultReducer} from '../reducers';
import {searchReducer} from 'search/reducers';

const initialState = {
    items: [],
    itemsById: {},
    matchedIds: [],
    aggregations: null,
    activeItem: null,
    previewItem: null,
    openItem: null,
    isLoading: false,
    totalItems: null,
    activeQuery: null,
    user: null,
    userType: null,
    userFolders: [],
    company: null,
    companyFolders: [],
    topics: [],
    newsOnlyFilterText: null,
    selectedItems: [],
    bookmarks: false,
    formats: [],
    newItems: [],
    newItemsByTopic: {},
    readItems: {},
    wire: {
        newsOnly: false,
    },
    search: searchReducer(),
    userSections: {},
    uiConfig: {},
    groups: [],
    searchInitiated: false,
    loadingAggregations: false,
    errorMessage : null,
};

function recieveItems(state, data) {
    const itemsById = Object.assign({}, state.itemsById);
    const items = data._items.map((item) => {
        itemsById[item._id] = item;
        item.deleted = false;
        return item._id;
    });

    const matchedIds = get(data, '_links.matched_ids.length') ?
        data._links.matched_ids :
        [];

    return {
        ...state,
        items,
        itemsById,
        matchedIds,
        isLoading: false,
        totalItems: data._meta.total,
        newItems: [],
        searchInitiated: false,
    };
}

function recieveAggs(state, data) {
    return {
        ...state,
        aggregations: data._aggregations || null,
        loadingAggregations: false,
    };
}

function markItemsRemoved(state, ids) {
    const itemsById = cloneDeep(state.itemsById || {});
    let activeItem = state.activeItem;
    let previewItem = state.previewItem;
    let openItem = state.openItem;

    (ids || []).forEach(
        (itemId) => {
            if (get(itemsById, itemId)) {
                itemsById[itemId].deleted = true;
            }

            if (activeItem === itemId) {
                activeItem = null;
            }

            if (previewItem === itemId) {
                previewItem = null;
            }

            if (get(openItem, '_id') === itemId) {
                openItem = null;
            }
        }
    );

    return {
        ...state,
        itemsById,
        activeItem,
        previewItem,
        openItem,
    };
}


function _wireReducer(state, action) {
    switch (action.type) {

    case TOGGLE_NEWS: {
        return {
            ...state,
            newsOnly: !state.newsOnly,
        };
    }

    case TOGGLE_SEARCH_ALL_VERSIONS: {
        return {
            ...state,
            searchAllVersions: !state.searchAllVersions,
        };
    }

    default:
        return state;
    }
}

export default function wireReducer(state = initialState, action) {
    switch (action.type) {

    case RECIEVE_ITEMS:
        return recieveItems(state, action.data);

    case RECIEVE_AGGS:
        return recieveAggs(state, action.data);

    case LOADING_AGGREGATIONS:
        return {...state, loadingAggregations: true};

    case INIT_DATA: {
        const navigations = get(action, 'wireData.navigations', []);
        const products = get(action, 'wireData.products', []);
        const user = get(action, 'wireData.user', {});

        return {
            ...state,
            readItems: action.readData || {},
            user: user._id,
            userType: user.user_type,
            userObject: user,
            userFolders: action.wireData.user_folders,
            topics: action.wireData.topics || [],
            company: action.wireData.company || null,
            companyFolders: action.wireData.company_folders,
            bookmarks: action.wireData.bookmarks || false,
            formats: action.wireData.formats || [],
            secondaryFormats: get(action, 'wireData.secondary_formats') || [],
            wire: Object.assign({}, state.wire, {
                newsOnly: action.newsOnly,
                searchAllVersions: action.searchAllVersions,
            }),
            search: Object.assign({}, state.search, {
                navigations,
                products,
            }),
            context: action.wireData.context || 'wire',
            savedItemsCount: action.wireData.saved_items || null,
            userSections: action.wireData.userSections || {},
            uiConfig: action.wireData.ui_config || {},
            groups: action.wireData.groups || [],
            newsOnlyFilterText: action.newsOnlyFilterText,
        };
    }

    case TOGGLE_NEWS:
    case TOGGLE_SEARCH_ALL_VERSIONS:
        return {...state, wire: _wireReducer(state.wire, action)};

    case WIRE_ITEM_REMOVED:
        return markItemsRemoved(state, action.ids);

    case SET_ERROR_MESSAGE:
        return {
            ...state,
            isLoading: false,
            errorMessage: action.message
        };

    case SET_ERROR: {
        return {...state,
            isLoading: false,
            errors: action.errors};
    }

    default:
        return defaultReducer(state || initialState, action);
    }
}
