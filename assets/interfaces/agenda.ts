import {AnyAction} from 'redux';
import {ThunkAction, ThunkDispatch} from 'redux-thunk';
import {IFilterGroup, IResourceItem, ISection} from './common';
import {IAgendaUIConfig} from './configs';
import {IUser, IUserType} from './user';
import {ITopic, ITopicFolder} from './topic';
import {ICompany} from './company';
import {IArticle} from './content';
import {ISearchState} from './search';

interface IPhoneNumber {
    public: boolean;
    number: string;
    usage?: string;
}

export interface IContact {
    _id: string;
    uri: string;
    public: boolean;
    first_name?: string;
    last_name?: string;
    postcode?: string;
    locality?: string;
    website?: string;
    notes?: string;
    organisation?: string;
    mobile?: Array<IPhoneNumber>;
    contact_phone?: Array<IPhoneNumber>;
    contact_email?: string[];
}

export interface ILocation {
    name: string;
    qcode: string;
    location?: {lat: number; lon: number};
    details?: string[];
    address?: {
        area?: string;
        locality?: string;
        country?: string;
        title?: string;
        line?: string[];
        postal_code?: string;
    };
}

export interface IEvent {
    _id: string;
    event_contact_info?: Array<IContact>;
    location?: Array<ILocation>;
    actioned_date?: string;
    _time_to_be_confirmed?: boolean;
    files?: Array<string>;
}

export type ICoverageStatus = 'coverage intended' |
    'coverage not planned' |
    'coverage not intended' |
    'coverage not decided' |
    'coverage not decided yet' |
    'coverage upon request';

export type ICoverageWorkflowStatus = 'draft' |
    'assigned' |
    'active' |
    'completed' |
    'cancelled';

export interface ICoverage {
    planning_id: IAgendaItem['_id'];
    coverage_id: IAgendaItem['_id'];
    scheduled: string;
    coverage_type: string;
    planning?: {
        scheduled: string;
    };
    watches?: Array<IUser['_id']>;
    coverage_status: ICoverageStatus;
    workflow_status: ICoverageWorkflowStatus;

    assigned_desk_name?: string;
    assigned_desk_email?: string;
    assigned_user_name?: string;
    assigned_user_email?: string;
    genre?: Array<{
        qcode: string,
        name: string
    }>;
    coverage_provider?: string;
}

export interface IAgendaItem extends IResourceItem {
    guid: string;
    type: 'agenda';
    item_type: 'event' | 'planning';
    event?: IEvent;
    location?: IEvent['location'];
    version?: number | string;
    plan?: IAgendaItem;
    planning_items?: Array<IAgendaItem>;
    _hits?: {
        matched_planning_items?: Array<IAgendaItem['_id']>;
        matched_coverages?: Array<ICoverage['coverage_id']>;
    };
    _display_from?: string;
    _display_to?: string;
    display_dates?: Array<{date: string}>;
    dates: {
        all_day?: boolean;
        no_end_time?: boolean;
        start: string;
        end?: string;
        tz?: string;
    };
    coverages?: Array<ICoverage>
    planning_date?: string;
    _time_to_be_confirmed?: boolean;
    name?: string;
    slugline?: string;
    headline?: string;
    description_text?: string;
    definition_short?: string;
    bookmarks?: Array<IUser['_id']>;
    watches?: Array<IUser['_id']>;
    es_highlight?: {[field: string]: Array<string>};
    state: string;
}

export interface IAgendaListGroup {
    date: string;
    items: Array<IAgendaItem['_id']>;
    hiddenItems: Array<IAgendaItem['_id']>;
}

export interface IAgendaListGroupItem {
    _id: IAgendaItem['_id'];
    group: IAgendaListGroup['date'];
    plan?: IAgendaItem['_id'];
}

export interface IAgendaState {
    items: Array<IAgendaItem['_id']>;
    fetchFrom: number;
    itemsById: {[itemId: string]: IAgendaItem};
    listItems: {
        groups: Array<IAgendaListGroup>;
        hiddenGroupsShown: {[dateString: string]: boolean};
    };
    aggregations?: {[field: string]: any}; // Too complex to even bother
    activeItem?: IAgendaListGroupItem;
    previewItem?: IAgendaItem['_id'];
    previewGroup?: string;
    previewPlan?: IAgendaItem['_id'];
    openItem?: IAgendaItem;
    isLoading: boolean;
    resultsFiltered: boolean;
    totalItems: number;
    activeQuery?: {[key: string]: any};
    user: IUser['_id'];
    userObject: IUser;
    userFolders: Array<ITopicFolder>;
    company?: ICompany['_id'];
    companyFolders: Array<ITopicFolder>;
    topics: Array<ITopic>;
    selectedItems: Array<IAgendaItem['_id']>;
    bookmarks: boolean;
    context: 'agenda';
    formats: Array<{
        format: string;
        name: string;
    }>;
    newItems: Array<IAgendaItem['_id']>;
    newItemsByTopic: {[topidId: string]: Array<IAgendaItem>};
    readItems: {[itemId: string]: number};
    agenda: {
        activeView: 'list-view' | 'list-view-compact';
        activeDate: number;
        activeGrouping: 'day'; // Week and month is partially supported in code, but never exposed in the UI
        eventsOnlyAccess: boolean;
        itemType?: 'events' | 'planning';
        featuredOnly: boolean;
        agendaWireItems: Array<IArticle>;
    };
    search: ISearchState;
    detail: boolean;
    userSections: {[sectionId: string]: ISection};
    searchInitiated: boolean;
    uiConfig: IAgendaUIConfig;
    groups: Array<IFilterGroup>;
    userType: IUserType;
    hasAgendaFeaturedItems: boolean;
    savedItemsCount: number;
    locators?: {
        _id: 'locators';
        items: Array<{
            name: string;
            state?: string;
            country?: string;
            world_region?: string;
        }>;
    };
    errors?: {[field: string]: Array<string>};
}

export type AgendaGetState = () => IAgendaState;
export type AgendaThunkAction<ReturnType = void> = ThunkAction<
    ReturnType,
    IAgendaState,
    unknown,
    AnyAction
>;
export type AgendaThunkDispatch = ThunkDispatch<IAgendaState, unknown, AnyAction>;
