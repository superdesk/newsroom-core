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
