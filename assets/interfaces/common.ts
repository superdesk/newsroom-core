import {IUser} from './user';
import {IArticle} from './content';
import {IAgendaItem, IAgendaState} from './agenda';

export type TDatetime = string; // ISO8601 format

export interface IFilterGroup {
    single?: boolean;
    field: string;
    label: string;
    nested?: {
        parent: string;
        field: string;
        value: string;
        include_planning?: boolean;
    };
}

export interface ISection {
    _id: string;
    name: string;
    group: string;
    search_type: string;
}

export interface ICountry {
    value: string;
    text: string;
}

interface IBaseAction {
    _id?: string;
    id: string;
    name: string;
    shortcut?: boolean;
    icon?: string;
    tooltip?: string;
    visited?(user: IUser['_id'], item: IArticle | IAgendaItem): void;
    when?(props: any, item: IArticle | IAgendaItem): boolean;
}

export interface ISingleItemAction extends IBaseAction {
    action(item?: IArticle | IAgendaItem, group?: string, plan?: IAgendaItem): void;
}

interface IMultiItemAction extends IBaseAction {
    multi: true;
    action(items?: Array<IArticle | IAgendaItem>): void;
}

export type IItemAction = ISingleItemAction | IMultiItemAction;

export interface IResourceItem {
    _id: string;
    _created: string;
    _updated: string;
    _etag: string;
    type: string;
}

export interface IRestApiResponse<T extends IResourceItem> {
    _items: Array<T>;
    _links: {};
    _meta: {
        max_results: number;
        page: number;
        total: number;
    };
    _aggregations: {[key: string]: any};
}

export interface ISubject {
    name: string;
    code: string;
    scheme: string;
}

export interface IOccurStatus {
    name: string;
    qcode: string;
    label: string;
}

export interface IDateFilter {
    name?: string,
    default?: boolean,
    filter?: string;
    query?: string;
}

export type IDateFilters = Array<IDateFilter>
