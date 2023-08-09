interface Window {
    sectionNames: {
        home: string;
        wire: string;
        agenda: string;
        monitoring: string;
        saved: string;
    };

    newsroom: {
        client_config: {
            debug: boolean;
            news_only_filter?: any;
        }
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
    companyReportsData: any;
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

    __REDUX_DEVTOOLS_EXTENSION_COMPOSE__: any;
}

declare module 'expect';
declare module 'alertifyjs';