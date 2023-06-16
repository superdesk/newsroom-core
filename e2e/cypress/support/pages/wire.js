import {AdvancedSearchForm} from '../forms/advancedSearch';

class WirePageWrapper {
    showAdvancedSearchModal() {
        cy.get('[data-test-id="show-advanced-search-panel-btn"]').click();
    }

    toggleSearchResultsBar() {
        cy.get('[data-test-id="search-results-bar"] [data-test-id="toggle-search-bar"]').click();
    }

    showSaveTopicModal() {
        cy.get('[data-test-id="save-topic-btn"]').click();
    }

    getSearchResultTags() {
        return cy.get('[data-test-id="search-result-tags"]');
    }
}

export const WirePage = new WirePageWrapper();
