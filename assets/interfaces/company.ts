import {TDatetime} from './common';
import {IUser} from './user';


export interface ICompany {
    _id: string;
    name: string;
    url?: string;
    sd_subscriber_id?: string;
    is_enabled: boolean;
    contact_name?: string;
    contact_email?: string;
    phone?: string;
    country?: string;
    expiry_date?: TDatetime;
    sections?: {[key: string]: boolean};
    archive_access?: boolean;
    events_only?: boolean;
    restrict_coverage_info?: boolean;
    company_type?: string;
    account_manager?: string;
    monitoring_administrator?: IUser['_id'];
    allowed_ip_list?: Array<string>;
    original_creator?: IUser['_id'];
    version_creator?: IUser['_id'];
    products?: Array<{
        _id: string;
        seats: number;
        section: 'wire' | 'agenda';
    }>;
    auth_domain?: string;
}
