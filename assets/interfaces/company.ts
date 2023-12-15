import {TDatetime} from './common';
import {IUser} from './user';

export interface IAuthProvider {
    _id: string;
    name: string;
    auth_type: string;
}

export interface ICompanyType {
    id: string;
    name: string;
}

export interface IService {
    name: string;
    code: string;
}

export interface ICompany {
    _id: string;
    name: string;
    url?: string;
    sd_subscriber_id?: string;
    is_enabled: boolean;
    is_approved?: boolean;
    contact_name?: string;
    contact_email?: string;
    phone?: string;
    country?: string;
    expiry_date?: TDatetime;
    sections?: {[key: string]: boolean};
    archive_access?: boolean;
    events_only?: boolean;
    restrict_coverage_info?: boolean;
    company_type?: ICompanyType['id'];
    company_size?: string;
    referred_by?: string;
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
    auth_provider?: IAuthProvider['_id']; // if not defined, system assumes a value of 'newshub'
}
