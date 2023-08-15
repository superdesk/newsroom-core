
export type TDatetime = string; // ISO8601 format

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
    dashboards: Array<{
        name: string;
        type: string;
        topic_ids: Array<ITopic['_id']>;
    }>;
    notification_schedule?: {
        timezone: string;
        times: Array<string>;
        last_run_time?: TDatetime;
    };
}

export type ITopicNotificationScheduleType = 'real-time' | 'scheduled' | null;

export interface ITopic {
    _id: string;
    label: string;
    query?: string;
    filter?: {[key: string]: any};
    created: string;
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

export interface ITopicFolder {
    _id: string;
    name: string;
    parent?: ITopicFolder['_id'];
    section: 'wire' | 'agenda' | 'monitoring';
}

export interface INavigation {
    _id: string;
    name: string;
    description?: string;
    is_enabled: boolean;
    order?: number;
    product_type: 'wire' | 'agenda';
    tile_images: Array<string>;
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
}
export interface IFilterGroup {
    field: string;
    label: string;
    nested?: {
        parent: string;
        field: string;
        value: string;
        include_planning?: boolean;
    };
}

export interface IClientConfig {
    advanced_search: {
        agenda: Array<string>;
        wire: Array<string>;
    };
    allow_companies_to_manage_products: boolean;
    company_expiry_alert_recipients?: string;
    coverage_request_recipients?: string;
    coverage_types: {[content_type: string]: {
        name: string;
        icon: string;
        translations?: {[language: string]: string};
    }};
    debug: boolean;
    default_language: string;
    default_timezone: string;
    display_abstract: boolean;
    display_agenda_featured_stories_only: boolean;
    display_all_versions_toggle: boolean;
    display_credits: boolean;
    display_news_only: boolean;
    filter_panel_defaults: {
        tab: {
            wire: string;
            agenda: string;
        };
        open: {
            wire: boolean;
            agenda: boolean;
        };
    };
    google_analytics?: string;
    google_maps_styles?: string;
    item_actions: {[key: string]: boolean};
    list_animations: boolean;
    locale_formats: {[language: string]: {
        COVERAGE_DATE_FORMAT?: string;
        COVERAGE_DATE_TIME_FORMAT?: string;
        DATE_FORMAT?: string;
        DATE_FORMAT_HEADER?: string;
        TIME_FORMAT?: string;
    }};
    monitoring_report_logo_path?: string;
    news_only_filter?: any;
    product_seat_request_recipients?: string;
    scheduled_notifications: {
        default_times: Array<string>;
    };
    system_alert_recipients?: string;
    wire_time_limit_days: number;
}
