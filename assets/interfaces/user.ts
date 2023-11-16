import {TDatetime} from './common';
import {ICompany} from './company';
import {ITopic} from './topic';

export interface IUserDashboard {
    type: string;
    name: string;
    topic_ids: Array<ITopic['_id']>;
}

export interface IUser {
    _id: string;
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    mobile: string;
    role: string;
    signup_details?: {[key: string]: any};
    country: string;
    company: ICompany['_id'];
    user_type: 'administrator' | 'internal' | 'public' | 'company_admin' | 'account_management';
    is_validated?: boolean;
    is_enabled?: boolean;
    is_approved?: boolean;
    expiry_alert?: boolean;
    receive_email?: boolean;
    receive_app_notifications?: boolean;
    locale: string;
    manage_company_topics?: boolean;
    last_active?: TDatetime;

    original_creator?: IUser['_id'];
    version_creator?: IUser['_id'];
    products: Array<{
        _id: string;
        section: 'wire' | 'agenda';
    }>;
    sections: {[key: string]: boolean};
    dashboards?: Array<IUserDashboard>;
    notification_schedule?: {
        timezone: string;
        times: Array<string>;
        last_run_time?: TDatetime;
    };
}

type IUserProfileEditable = Pick<IUser, 'first_name' | 'last_name' | 'phone' | 'mobile' | 'role' | 'locale' | 'receive_email' | 'receive_app_notifications'>;
export type IUserProfileUpdates = Partial<IUserProfileEditable>;