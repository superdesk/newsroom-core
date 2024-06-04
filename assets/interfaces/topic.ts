import {IUser} from './user';
import {ICompany} from './company';
import {ISearchState} from './search';

export type ITopicNotificationScheduleType = 'real-time' | 'scheduled' | null;

export interface ITopicFolder {
    _id: string;
    name: string;
    parent?: ITopicFolder['_id'];
    section: 'wire' | 'agenda' | 'monitoring';
    _etag?: string;
    _created?: string;
    _updated?: string;
}

export type ISearchFields = Array<string>;

export interface ISearchParams {
    query?: string;
    filter?: {
        [field: string]: string[];
    };
    timezone_offset?: number;
    topic_type: 'wire' | 'agenda';
    navigation: Array<string>;
    // if `advanced` is defined, make sure `fields` is mandatory and all others are not
    advanced?: {fields: ISearchState['advanced']['fields']} & Partial<Omit<ISearchState['advanced'], 'fields'>>;
    created?: {
        from?: string | null;
        to?: string | null;
    };
    product: ISearchState['productId'];
    sortQuery: ISearchState['activeSortQuery'];
}

export interface ITopic extends ISearchParams {
    _id: string;
    _etag: string;
    _created: string;
    _updated: string;
    label: string;
    description?: string;
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
    user: IUser['_id'];
    company: ICompany['_id'];
    is_global?: boolean;
    subscribers: Array<{
        user_id: IUser['_id'];
        notification_type: ITopicNotificationScheduleType;
    }>;
    folder?: ITopicFolder['_id'] | null;
}
