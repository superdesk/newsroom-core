import {IUser} from './user';
import {ICompany} from './company';

export type ITopicNotificationScheduleType = 'real-time' | 'scheduled' | null;

export interface ITopicFolder {
    _id: string;
    name: string;
    parent?: ITopicFolder['_id'];
    section: 'wire' | 'agenda' | 'monitoring';
}

export interface ITopic {
    _id: string;
    label: string;
    query?: string;
    filter?: Dictionary<string>;
    created: Dictionary<string>;
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
    user: IUser['_id'];
    company: ICompany['_id'];
    is_global?: boolean;
    subscribers: Array<{
        user_id: IUser['_id'];
        notification_type: ITopicNotificationScheduleType;
    }>;
    timezone_offset?: number;
    topic_type: 'wire' | 'agenda';
    navigation: Array<string>;
    folder?: ITopicFolder['_id'] | null;
    advanced?: {
        fields: Array<string>;
        all: string;
        any: string;
        exclude: string;
    };
}
