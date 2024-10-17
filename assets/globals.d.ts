interface IClientConfig {
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
    display_author_role: boolean;
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
    view_content_tooltip_email?: string;
    searchbar_threshold_value?: number;
    agenda_top_story_scheme?: string;
    wire_labels_scheme?: string;
    coverage_status_filter?: {
        [key: string]: {
            enabled: boolean;
            option_label: string;
            button_label: string;
        }
    };
    agenda_sort_events_with_coverage_on_top?: boolean;
    collapsed_search_by_default?: boolean;
    show_user_register?: boolean;
    multimedia_website_search_url?: string;
    show_default_time_frame_label?: boolean;
}

interface Window {
    sectionNames: {
        home: string;
        wire: string;
        agenda: string;
        monitoring: string;
        saved: string;
    };

    newsroom: {
        client_config: IClientConfig;
        websocket?: any;
    };

    locale: any;
    gtag: any;
    analytics: any;
    google: any;
    iframely: any;
    translations: any;
    profileData: any;
    wireData: any;
    homeData: any;
    agendaData: any;
    amNewsData: any;
    viewData: any;
    report: any;
    factCheckData: any;
    mapsLoaded: any;
    googleMapsKey: any;
    mediaReleasesData: any;
    notificationData: any;
    twttr: any;
    instgrm: any;
    locales: any;
    marketPlaceData: {
        home_page: any;
    };
    restrictedActionModalBody: string;

    __REDUX_DEVTOOLS_EXTENSION_COMPOSE__: any;
    sitename: string;
}

type Dictionary<T> = {[key: string]: T};

declare module 'expect';
declare module 'alertifyjs';
