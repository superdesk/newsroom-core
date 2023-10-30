import {IAgendaItem} from './agenda';
import {IUser} from './user';

export type IContentType = 'text' | 'picture' | 'video' | 'audio';

export interface IRendition {
    href: string;
    mimetype: string;
    media?: string;
    width?: number;
    height?: number;
}

export interface IArticle {
    _id: string;
    guid: string;
    type: IContentType;
    ancestors?: Array<IArticle['_id']>;
    nextversion?: IArticle['_id'];
    associations?: {[key: string]: IArticle};
    renditions?: {[key: string]: IRendition};
    slugline: string;
    headline: string;
    anpa_take_key?: string;
    source: string;
    versioncreated: string;
    extra?: {[key: string]: any};
    es_highlight?: {[field: string]: string}
}

interface IBaseAction {
    name: string;
    shortcut: boolean;
    icon: string;
    tooltip: string;
    multi: boolean;
    visited?(user: IUser['_id'], item: IArticle): void;
}

interface ISingleItemAction extends IBaseAction {
    multi: false;
    action(item: IArticle, group: string, plan: IAgendaItem): void;
}

interface IMultiItemAction extends IBaseAction {
    multi: true;
    action(items: Array<IArticle>): void;
}

export type IItemAction = ISingleItemAction | IMultiItemAction;
