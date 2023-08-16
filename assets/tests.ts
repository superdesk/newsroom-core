/* eslint-env node */

// Create the `client_config` for tests, otherwise test console output is filled with
// `Client config is not yet available for key` messages
window.newsroom = {
    client_config: {
        advanced_search: {
            agenda: ['name', 'headline', 'slugline', 'description'],
            wire: ['headline', 'slugline', 'body_html'],
        },
        allow_companies_to_manage_products: false,
        coverage_types: {
            text: {name: 'Text', icon: 'text'},
            photo: {name: 'Photo', icon: 'photo'},
            picture: {name: 'Picture', icon: 'photo'},
            audio: {name: 'Audio', icon: 'audio'},
            video: {name: 'Video', icon: 'video'},
            explainer: {name: 'Explainer', icon: 'explainer'},
            infographics: {name: 'Infographics', icon: 'infographics'},
            graphic: {name: 'Graphic', icon: 'infographics'},
            live_video: {name: 'Live Video', icon: 'live-video'},
            live_blog: {name: 'Live Blog', icon: 'live-blog'},
            video_explainer: {name: 'Video Explainer', icon: 'explainer'},
        },
        debug: true,
        default_language: 'en',
        default_timezone: 'Australia/Sydney',
        display_abstract: false,
        display_agenda_featured_stories_only: true,
        display_all_versions_toggle: false,
        display_credits: false,
        display_news_only: true,
        filter_panel_defaults: {
            tab: {
                wire: 'nav',
                agenda: 'nav',
            },
            open: {
                wire: false,
                agenda: false,
            },
        },
        item_actions: {},
        list_animations: true,

        locale_formats: {
            en: {
                TIME_FORMAT: 'HH:mm',
                DATE_FORMAT: 'DD-MM-YYYY',
                COVERAGE_DATE_TIME_FORMAT: 'HH:mm DD/MM',
                COVERAGE_DATE_FORMAT: 'DD/MM',
                DATE_FORMAT_HEADER: 'EEEE, dd/MM/yyyy',
            },
            fr_CA: {
                DATE_FORMAT: 'DD/MM/YYYY',
                DATE_FORMAT_HEADER: 'EEEE, \'le\' d MMMM yyyy',
            },
        },

        scheduled_notifications: {
            default_times: [
                '07:00',
                '15:00',
                '19:00',
            ],
        },
        system_alert_recipients: '',
        wire_time_limit_days: 0,
    },
};

// populate section names with defaults
window.sectionNames = {
    home: 'Home',
    wire: 'Wire',
    agenda: 'Agenda',
    monitoring: 'Monitoring',
    saved: 'Saved / Watched',
};

const testsContext = require.context('.', true, /[Ss]pec.(ts|tsx)$/);

testsContext.keys().forEach(testsContext);
