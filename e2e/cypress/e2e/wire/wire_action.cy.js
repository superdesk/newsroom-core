import {setup, addDefaultResources, addResources, addAllWireItems} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';

export const WIRE_ITEMS = {
    syd_weather_1: {
        _id: 'urn:localhost:syd-weather-1',
        type: 'text',
        version: 1,
        versioncreated: new Date(),
        headline: 'Sydney Weather',
        slugline: 'weather',
        body_html: '<p><h1>Sydney Weather</h1></p>',
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
        versioncreated: '2023-06-04T12:00:00+0000',
        headline: 'Brisbane Traffic',
        slugline: 'traffic',
        body_html: '<p><h1>Brisbane Traffic</h1></p>',
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
};

describe('wire - filters', () => {
    beforeEach(() => {
        setup();
        addDefaultResources();
        addResources([{
            resource: 'items',
            use_resource_service: false,
            items: [
                WIRE_ITEMS.syd_weather_1,
                WIRE_ITEMS.bris_traffic_1,
            ],
        }]);
        NewshubLayout.login('admin@example.com', 'admin');
    });

    it('can search using navigation & filters', () => {
        /**
            SEARCH
        */
        cy.get('[data-test-id="sidenav-link-wire"]').click();
        cy.get('[data-test-id="top-search-bar"]').click().type('Sydney');
        cy.get('[data-test-id="search-submit-button"]').click();

        cy.url().should('include', 'Sydney');

        cy.get(`[data-test-id="wire-item"][data-test-value="${WIRE_ITEMS.syd_weather_1._id}"]`).should('exist');
        cy.get(`[data-test-id="wire-item"][data-test-value="${WIRE_ITEMS.bris_traffic_1._id}"]`).should('not.exist');

        cy.get('[data-test-id="top-search-bar"] form input').clear().type("{enter}");
        cy.url().should('not.include', 'Sydney');

        cy.get(`[data-test-id="wire-item"][data-test-value="${WIRE_ITEMS.syd_weather_1._id}"]`).should('exist');
        cy.get(`[data-test-id="wire-item"][data-test-value="${WIRE_ITEMS.bris_traffic_1._id}"]`).should('exist');

        /**
            FILTERS
        */
        cy.get('[data-test-id="sidenav-link-wire"]').click();
        cy.get('[data-test-id="toggle-filter-panel"]').click();
        cy.get('[data-test-id="filter-panel-tab--filters"]').click();

        /**
            check filtering by checkboxes
        */
        cy.get(`[data-test-id="checkbox"][data-test-value="${WIRE_ITEMS.syd_weather_1.service[0].name}"] input`).check();
        cy.get('[data-test-id="filter-panel--search-btn"]').click();

        cy.url().should('include', `${WIRE_ITEMS.syd_weather_1.service[0].name}`);

        cy.get(`[data-test-id="wire-item"][data-test-value="${WIRE_ITEMS.syd_weather_1._id}"]`).should('exist');
        cy.get(`[data-test-id="wire-item"][data-test-value="${WIRE_ITEMS.bris_traffic_1._id}"]`).should('not.exist');

        cy.get('[data-test-id="filter-panel--clear-btn"]').click();

        /**
            check filtering by date input
        */
        cy.get('[data-test-id="nav-link--today"]').click();
        cy.get('[data-test-id="filter-panel--search-btn"]').click();

        cy.get(`[data-test-id="wire-item"][data-test-value="${WIRE_ITEMS.syd_weather_1._id}"]`).should('exist');
        cy.get(`[data-test-id="wire-item"][data-test-value="${WIRE_ITEMS.bris_traffic_1._id}"]`).should('not.exist'); 
    });
});
