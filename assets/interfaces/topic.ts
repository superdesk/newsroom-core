import {IUser} from './user';

export interface ITopic {
    _id: string;
    label: string;
    query?: string;
    filter?: Dictionary<string>;
    created?: Dictionary<string>;
    user: IUser['_id'];
    company: any;
    is_global?: boolean;
    subscribers: Array<IUser['_id']>;
    timezone_offset?: number;
    topic_type: 'wire' | 'agenda';
    navigation?: Array<string>;
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
    folder: string;
    advanced?: Dictionary<string>;
}