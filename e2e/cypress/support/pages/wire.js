import {SearchResultsBar} from '../containers/searchResultsBar';
import {FilterPanelContainer} from '../containers/filterPanel';

class WirePageWrapper {
    constructor() {
        this.searchResults = new SearchResultsBar();
        this.filterPanel = new FilterPanelContainer();
    }

    item(value) {
        return cy.get(`[data-test-id="wire-item"][data-test-value="${value}"]`);
    }

    showAdvancedSearchModal() {
        cy.get('[data-test-id="show-advanced-search-panel-btn"]').click();
    }

    showSaveTopicModal() {
        this.searchResults
            .getSearchResultElement('topics', '[data-test-id="save-topic-btn"]')
            .click();
    }

    getTopSearchBarInput() {
        return cy.get('[data-test-id="top-search-bar"] input');
    }

    openSideNav() {
        cy.get('[data-test-id="sidenav-link-wire"]').click();
    }

    search(value) {
        cy.get('[data-test-id="top-search-bar"]').click().type(value);
        cy.get('[data-test-id="search-submit-button"]').click();
    }
}

export const WirePage = new WirePageWrapper();
