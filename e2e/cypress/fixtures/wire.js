import moment from 'moment/moment';

export const WIRE_ITEMS = {
    syd_weather_1: {
        _id: 'urn:localhost:syd-weather-1',
        type: 'text',
        version: 1,
        versioncreated: moment(),
        headline: 'Sydney Weather Today Current',
        slugline: 'current-weather-today wire',
        body_html: '<p><h1>Sydney Weather Report for Today</h1></p>',
        genre: [{code: 'Article', name: 'Article (news)'}],
        subject: [{code: '01001000', name: 'archaeology'}],
        service: [{code: 'weather', name: 'Weather'}],
        place: [{code: 'NSW', name: 'New South Wales'}],
        urgency: 3,
        priority: 6,
        language: 'en',
        pubstatus: 'usable',
        source: 'sofab',
    },
    bris_traffic_1: {
        _id: 'urn:localhost:bris-traffic-1',
        type: 'text',
        version: 1,
        versioncreated: moment(),
        headline: 'Brisbane Traffic Today Current',
        slugline: 'current-traffic-today wire',
        body_html: '<p><h1>Brisbane Traffic Report for Today</h1></p>',
        genre: [{code: 'Article', name: 'Article (news)'}],
        subject: [{code: '01001000', name: 'archaeology'}],
        service: [{code: 'traffic', name: 'Traffic'}],
        place: [{code: 'QLD', name: 'Queensland'}],
        urgency: 3,
        priority: 5,
        language: 'en',
        pubstatus: 'usable',
        source: 'sofab',
    },
    bris_traffic_2: {
        _id: 'urn:localhost:bris-traffic-2',
        type: 'text',
        version: 1,
        versioncreated: "2024-06-04T12:00:00+0000",
        headline: 'Current Elections take placed',
        slugline: 'Electionsssss',
        body_html: '<p><h1>Brisbane Traffic Report for Today</h1></p>',
        genre: [{code: 'Article', name: 'Article (news)'}],
        subject: [{code: '01001000', name: 'archaeology'}],
        service: [{code: 'traffic', name: 'Traffic'}],
        place: [{code: 'QLD', name: 'Queensland'}],
        urgency: 3,
        priority: 5,
        language: 'en',
        pubstatus: 'usable',
        source: 'sofab',
    },
}
