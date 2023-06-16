import {
    SET_EVENT_QUERY,
    RECIEVE_ITEMS,
    INIT_DATA,
    SELECT_DATE,
    WATCH_EVENTS,
    STOP_WATCHING_EVENTS,
    UPDATE_ITEM,
    TOGGLE_FEATURED_FILTER,
    SET_ITEM_TYPE_FILTER,
    AGENDA_WIRE_ITEMS,
    WATCH_COVERAGE,
    STOP_WATCHING_COVERAGE,
    SET_ERROR_MESSAGE,
    SET_ERROR
} from './actions';

import {get, uniq} from 'lodash';
import {EXTENDED_VIEW} from 'wire/defaults';
import {searchReducer} from 'search/reducers';
import {defaultReducer} from '../reducers';
import {EARLIEST_DATE} from './utils';

const initialState = {
    items: [],
    itemsById: {},
    aggregations: null,
    activeItem: null,
    previewItem: null,
    previewGroup: null,
    previewPlan: null,
    openItem: null,
    isLoading: false,
    resultsFiltered: false,
    totalItems: null,
    activeQuery: null,
    user: null,
    userFolders: [],
    company: null,
    companyFolders: [],
    topics: [],
    selectedItems: [],
    bookmarks: false,
    context: null,
    formats: [],
    newItems: [],
    newItemsByTopic: {},
    readItems: {},
    agenda: {
        activeView: EXTENDED_VIEW,
        activeDate: Date.now(),
        activeGrouping: 'day',
        eventsOnlyAccess: false,
        itemType: null,
        featuredOnly: false,
        agendaWireItems: [],
    },
    search: searchReducer(),
    detail: false,
    userSections: {},
    searchInitiated: false,
    uiConfig: {},
    groups: [],
    hasAgendaFeaturedItems: false,
    errorMessage: null
};

function recieveItems(state, data) {
    const itemsById = Object.assign({}, state.itemsById);
    const items = data._items.map((item) => {
        itemsById[item._id] = item;
        return item._id;
    });

    return {
        ...state,
        items,
        itemsById,
        isLoading: false,
        totalItems: data._meta.total,
        aggregations: data._aggregations || null,
        newItems: [],
        searchInitiated: false,
    };
}

function _agendaReducer(state, action) {
    switch (action.type) {

    case SELECT_DATE:
        return {
            ...state,
            selectedItems: [],
            activeDate: action.dateString,
            activeGrouping: action.grouping || 'day',
        };

    default:
        return state;
    }
}

export default function agendaReducer(state = initialState, action) {
    switch (action.type) {

    case RECIEVE_ITEMS:
        return recieveItems(state, action.data);

    case SET_EVENT_QUERY:
        return {...state, query: action.query, activeItem: null};

    case WATCH_EVENTS: {
        const itemsById = Object.assign({}, state.itemsById);
        action.items.forEach((_id) => {
            const watches = get(itemsById[_id], 'watches', []).concat(state.user);
            itemsById[_id] = Object.assign({}, itemsById[_id], {watches});
            (get(itemsById[_id], 'coverages') || []).forEach((c) => {
                if (get(c, 'watches.length', 0) > 0) {
                    c.watches = [];
                }
            });
        });

        return {...state, itemsById};
    }

    case WATCH_COVERAGE: {
        const itemsById = Object.assign({}, state.itemsById);
        const item = itemsById[get(action, 'item._id')];
        const coverage = (get(item, 'coverages') || []).find((c) => c.coverage_id === action.coverage.coverage_id);
        if (coverage) {
            coverage['watches'] = uniq([
                ...(get(coverage, 'watches') || []),
                state.user
            ]);
        }

        return {...state, itemsById};
    }

    case STOP_WATCHING_COVERAGE: {
        const itemsById = Object.assign({}, state.itemsById);
        const item = itemsById[get(action, 'item._id')];
        const coverage = (get(item, 'coverages') || []).find((c) => c.coverage_id === action.coverage.coverage_id);
        if (coverage) {
            coverage['watches'] = (get(coverage, 'watches') || []).filter((u) => u !== state.user);
        }

        return {...state, itemsById};
    }

    case STOP_WATCHING_EVENTS: {
        const itemsById = Object.assign({}, state.itemsById);
        action.items.forEach((_id) => {
            const watches = get(itemsById[_id], 'watches', []).filter((userId) => userId !== state.user);
            itemsById[_id] = Object.assign({}, itemsById[_id], {watches});
        });

        return {...state, itemsById};
    }

    case UPDATE_ITEM: {
        // Update existing items, remove killed items
        let itemsById = Object.assign({}, state.itemsById);
        let updatedItems = [ ...state.items ];
        const item = action.item;
        if(itemsById[item._id]) {
            if (get(item, 'state') === 'killed') {
                delete itemsById[item._id];
                updatedItems = updatedItems.filter((i) => i !== item._id);
            } else {
                itemsById[item._id] = item;
            }
        }

        return {
            ...state,
            itemsById: itemsById,
            items: updatedItems,
        };
    }

    case INIT_DATA: {
        const navigations = get(action, 'agendaData.navigations', []);
        const openItem = get(action, 'agendaData.item', null);
        const agenda = {
            ...state.agenda,
            activeDate: action.agendaData.bookmarks ? EARLIEST_DATE : action.activeDate || state.agenda.activeDate,
            eventsOnlyAccess: action.agendaData.events_only,
            restrictCoverageInfo: action.agendaData.restrict_coverage_info,
            featuredOnly: action.featuredOnly,
        };

        return {
            ...state,
            readItems: action.readData || {},
            user: (action.agendaData.user || {})._id || null,
            userObject: action.agendaData.user,
            topics: action.agendaData.topics || [],
            company: action.agendaData.company || null,
            bookmarks: action.agendaData.bookmarks || false,
            formats: action.agendaData.formats || [],
            search: Object.assign({}, state.search, {navigations}),
            context: 'agenda',
            openItem: openItem,
            detail: !!openItem,
            agenda,
            savedItemsCount: action.agendaData.saved_items || null,
            userSections: action.agendaData.userSections || {},
            locators: action.agendaData.locators || null,
            uiConfig: action.agendaData.ui_config || {},
            groups: action.agendaData.groups || [],
            hasAgendaFeaturedItems: action.agendaData.has_agenda_featured_items || false,
            userFolders: action.agendaData.user_folders,
            companyFolders: action.agendaData.company_folders,
        };
    }

    case SELECT_DATE:
        return {
            ...state,
            activeItem: null,
            previewItem: null,
            agenda: _agendaReducer(state.agenda, action)
        };

    case TOGGLE_FEATURED_FILTER:
        return {
            ...state,
            agenda: {
                ...state.agenda,
                featuredOnly: !state.agenda.featuredOnly,
            }
        };
    case SET_ITEM_TYPE_FILTER:
        return {
            ...state,
            agenda: {
                ...state.agenda,
                itemType: action.value,
            },
        };

    case AGENDA_WIRE_ITEMS:
        return {
            ...state,
            agenda: {
                ...state.agenda,
                agendaWireItems: action.items
            }
        };

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
