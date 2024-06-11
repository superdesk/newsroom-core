import {setup, addDefaultResources, addResources} from '../../support/e2e';
import {WirePage} from '../../support/pages/wire'
import {FilterPanel} from '../../support/pages/filter_panel'
import {NewshubLayout} from '../../support/pages/layout';
import {WIRE_ITEMS} from '../../fixtures/wire'

const WireItems = {
    item_1: WIRE_ITEMS.syd_weather_1,
    item_2: WIRE_ITEMS.bris_traffic_1,
    item_3: WIRE_ITEMS.bris_traffic_2,
};

describe('wire - filters', () => {
    beforeEach(() => {
        setup();
        addDefaultResources();
        addResources([{
            resource: 'items',
            use_resource_service: false,
            items: [
                WireItems.item_1,
                WireItems.item_2,
                WireItems.item_3,
            ],
        }]);
        NewshubLayout.login('admin@example.com', 'admin');
    });

    it('can search using navigation & filters', () => {
        /**
            SEARCH
        */
        WirePage.openSideNav();
        WirePage.search('Sydney');

        cy.url().should('include', 'Sydney');

        WirePage.item(WireItems.item_1._id).should('exist');
        WirePage.item(WireItems.item_2._id).should('not.exist');

        cy.get('[data-test-id="top-search-bar"] form input').clear().type("{enter}");
        cy.url().should('not.include', 'Sydney');

        WirePage.item(WireItems.item_1._id).should('exist');
        WirePage.item(WireItems.item_2._id).should('exist');

        /**
            FILTERS
        */
        FilterPanel.openPanel();
        FilterPanel.openFiltersTab();

        /**
            check filtering by checkboxes
        */
        FilterPanel.selectFilter(WireItems.item_1.service[0].name);
        FilterPanel.button('search');

        cy.url().should('include', `${WireItems.item_1.service[0].name}`);

        WirePage.item(WireItems.item_1._id).should('exist');
        WirePage.item(WireItems.item_2._id).should('not.exist');

        FilterPanel.button('clear');

        /**
            check filtering by date input
        */
        cy.get('[data-test-id="date-filter-select"]').should('have.value', 'last_30_days');

        WirePage.item(WireItems.item_1._id).should('exist');
        WirePage.item(WireItems.item_2._id).should('exist');

        const fromDate = '2024-06-03';
        const toDate = '2024-06-05';

        cy.get('[data-test-id="date-filter-select"]').select('custom_date');
        cy.get('[data-test-id="custom-date-from"]').type(fromDate);
        cy.get('[data-test-id="custom-date-to"]').type(toDate);
        FilterPanel.button('search');

        // Add assertions to verify the items displayed based on the custom date range
        WirePage.item(WireItems.item_3._id).should('exist');
    });
});
