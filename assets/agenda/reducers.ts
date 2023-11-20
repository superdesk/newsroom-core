import {get, uniq} from 'lodash';

import {
    IAgendaItem,
    IAgendaListGroup,
    IRestApiResponse,
    IAgendaState,
} from 'interfaces';
import {
    RECIEVE_ITEMS,
    SET_LIST_GROUPS_AND_ITEMS,
    ADD_ITEMS_TO_LIST_GROUPS,
    SET_LIST_GROUP_HIDDEN_ITEMS,
    TOGGLE_HIDDEN_GROUP_ITEMS,
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
    SET_ERROR,
    SET_LOADING_HIDDEN_ITEMS,
    RECIEVE_NEXT_ITEMS,
} from './actions';

import {EXTENDED_VIEW} from 'wire/defaults';
import {searchReducer} from 'search/reducers';
import {defaultReducer} from '../reducers';
import {EARLIEST_DATE} from './utils';

const initialState: IAgendaState = {
    items: [],
    fetchFrom: 0,
    itemsById: {},
    listItems: {
        groups: [],
        hiddenGroupsShown: {},
        hiddenItemsLoading: false,
    },
    aggregations: undefined,
    activeItem: undefined,
    previewItem: undefined,
    previewGroup: undefined,
    previewPlan: undefined,
    openItem: undefined,
    isLoading: false,
    resultsFiltered: false,
    totalItems: 0,
    activeQuery: undefined,
    // Use `window.agendaData` so these attributes always have a value
    user: window.agendaData.user._id,
    userObject: window.agendaData.user,
    userType: window.agendaData.user.user_type ?? 'public',

    userFolders: [],
    company: undefined,
    companyFolders: [],
    topics: [],
    selectedItems: [],
    bookmarks: false,
    context: 'agenda',
    formats: [],
    newItems: [],
    newItemsByTopic: {},
    readItems: {},
    agenda: {
        activeView: EXTENDED_VIEW,
        activeDate: Date.now(),
        activeGrouping: 'day',
        eventsOnlyAccess: false,
        itemType: undefined,
        featuredOnly: false,
        agendaWireItems: [],
    },
    search: searchReducer(undefined, undefined, 'agenda'),
    detail: false,
    userSections: {},
    searchInitiated: false,
    uiConfig: {_id: 'agenda'},
    groups: [],
    hasAgendaFeaturedItems: false,
    savedItemsCount: 0,
};

function recieveItems(state: IAgendaState, data: IRestApiResponse<IAgendaItem>): IAgendaState {
    const itemsById = Object.assign({}, state.itemsById);
    const items = data._items.map((item) => {
        itemsById[item._id] = item;
        return item._id;
    });

    return {
        ...state,
        items,
        fetchFrom: items.length,
        itemsById,
        listItems: {
            ...state.listItems,
            groups: [],
        },
        isLoading: false,
        totalItems: data._meta.total,
        aggregations: data._aggregations || undefined,
        newItems: [],
        searchInitiated: false,
    };
}

function updateListGroups(state: IAgendaState, updatedGroups: Array<IAgendaListGroup>): IAgendaState {
    const updatedGroupsById = updatedGroups.reduce<{[date: string]: IAgendaListGroup}>((groups, group) => {
        groups[group.date] = group;

        return groups;
    }, {});
    const currentGroupsById = state.listItems.groups.reduce<{[date: string]: IAgendaListGroup}>((groups, group) => {
        groups[group.date] = group;

        return groups;
    }, {});

    return {
        ...state,
        listItems: {
            ...state.listItems,
            groups: uniq([
                ...Object.keys(currentGroupsById),
                ...Object.keys(updatedGroupsById),
            ]).sort().map((groupId) => ({
                ...currentGroupsById[groupId] ?? {},
                items: uniq([
                    ...currentGroupsById[groupId]?.items ?? [],
                    ...updatedGroupsById[groupId]?.items ?? [],
                ]),
                hiddenItems: uniq([
                    ...currentGroupsById[groupId]?.hiddenItems ?? [],
                    ...updatedGroupsById[groupId]?.hiddenItems ?? [],
                ]),
                date: groupId,
            })),
        },
    };
}

function runDefaultReducer(state: IAgendaState, action: any): IAgendaState {
    const newState: IAgendaState = defaultReducer(state || initialState, action);

    if (action.type === RECIEVE_NEXT_ITEMS && action.data.setFromSearch) {
        // increment the `fetchFrom` number with the length of the API response
        newState.fetchFrom += (action.data as IRestApiResponse<IAgendaItem>)._items.length;
    }

    return newState;
}

export default function agendaReducer(state: IAgendaState = initialState, action: any): IAgendaState {
    switch (action.type) {

    case RECIEVE_ITEMS:
        return recieveItems(state, action.data);

    case SET_LOADING_HIDDEN_ITEMS:
        return {
            ...state,
            listItems: {
                ...state.listItems,
                hiddenItemsLoading: action.data,
            },
        };

    case SET_LIST_GROUPS_AND_ITEMS:
        return {
            ...state,
            listItems: {
                ...state.listItems,
                groups: action.data,
            },
        };

    case ADD_ITEMS_TO_LIST_GROUPS:
        return updateListGroups(state, action.data);

    case SET_LIST_GROUP_HIDDEN_ITEMS:
        return updateListGroups(state, action.data);

    case TOGGLE_HIDDEN_GROUP_ITEMS:
        return {
            ...state,
            listItems: {
                ...state.listItems,
                hiddenGroupsShown: {
                    ...state.listItems.hiddenGroupsShown,
                    [action.data]: !state.listItems.hiddenGroupsShown[action.data],
                },
            },
        };

    case WATCH_EVENTS: {
        const itemsById = Object.assign({}, state.itemsById);
        action.items.forEach((itemId: string) => {
            if (itemsById[itemId] == null) {
                return;
            }

            itemsById[itemId] = {
                ...itemsById[itemId],
                watches: [
                    ...itemsById[itemId].watches ?? [],
                    state.user,
                ],
            };

            (itemsById[itemId].coverages ?? []).forEach((coverage) => {
                coverage.watches = [];
            });
        });

        return {...state, itemsById};
    }

    case WATCH_COVERAGE: {
        const itemsById = Object.assign({}, state.itemsById);
        const item = itemsById[get(action, 'item._id')];
        const coverage = (get(item, 'coverages') || []).find((c: any) => c.coverage_id === action.coverage.coverage_id);
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
        const coverage = (get(item, 'coverages') || []).find((c: any) => c.coverage_id === action.coverage.coverage_id);
        if (coverage) {
            coverage['watches'] = (get(coverage, 'watches') || []).filter((u: any) => u !== state.user);
        }

        return {...state, itemsById};
    }

    case STOP_WATCHING_EVENTS: {
        const itemsById = Object.assign({}, state.itemsById);
        action.items.forEach((_id: any) => {
            const watches = get(itemsById[_id], 'watches', []).filter((userId: any) => userId !== state.user);
            itemsById[_id] = Object.assign({}, itemsById[_id], {watches});
        });

        return {...state, itemsById};
    }

    case UPDATE_ITEM: {
        // Update existing items, remove killed items
        const itemsById = Object.assign({}, state.itemsById);
        let updatedItems = [ ...state.items ];
        const item = action.item;
        if(itemsById[item._id]) {
            if (get(item, 'state') === 'killed') {
                delete itemsById[item._id];
                updatedItems = updatedItems.filter((i: any) => i !== item._id);
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
        const agenda: any = {
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
            userObject: action.agendaData.user || {},
            userType: (action.agendaData.user || {}).user_type || null,
            topics: action.agendaData.topics || [],
            company: action.agendaData.company || null,
            bookmarks: action.agendaData.bookmarks || false,
            formats: action.agendaData.formats || [],
            search: Object.assign({}, state.search, {navigations}),
            context: 'agenda',
            openItem: openItem,
            detail: !!openItem,
            agenda,
            savedItemsCount: action.agendaData.saved_items || 0,
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
            activeItem: undefined,
            previewItem: undefined,
            selectedItems: [],
            agenda: {
                ...state.agenda,
                activeDate: action.dateString,
                activeGrouping: action.grouping || 'day',
            },
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

    case SET_ERROR: {
        return {...state,
            isLoading: false,
            errors: action.errors};
    }
    default:
        return runDefaultReducer(state, action);
    }
}
