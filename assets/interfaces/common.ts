import {IUser} from './user';
import {IArticle} from './content';
import {IAgendaItem} from './agenda';

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

export type IListConfig = {[key: string]: string | number | boolean};

interface IBaseAction {
    _id: string;
    id: string;
    name: string;
    shortcut: boolean;
    icon: string;
    tooltip: string;
    multi: boolean;
    visited?(user: IUser['_id'], item: IArticle | IAgendaItem): void;
    when?(props: any, item: IArticle | IAgendaItem): boolean;
}

interface ISingleItemAction extends IBaseAction {
    multi: false;
    action(item: IArticle | IAgendaItem, group: string, plan: IAgendaItem): void;
}

interface IMultiItemAction extends IBaseAction {
    multi: true;
    action(items: Array<IArticle | IAgendaItem>): void;
}

export type IItemAction = ISingleItemAction | IMultiItemAction;
