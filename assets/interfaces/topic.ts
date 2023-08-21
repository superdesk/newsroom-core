import {IUser} from './user';
import {ICompany} from './company';

export type ITopicNotificationScheduleType = 'real-time' | 'scheduled' | null;

export interface ITopicFolder {
    _id: string;
    name: string;
    parent?: ITopicFolder['_id'];
    section: 'wire' | 'agenda' | 'monitoring';
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
    advanced?: {
        all: string;
        any: string;
        exclude: string;
        fields: ISearchFields;
    };
    created?: {
        from?: string | null;
        to?: string | null;
    };
}

export interface ITopic extends ISearchParams {
    _id: string;
    label: string;
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
