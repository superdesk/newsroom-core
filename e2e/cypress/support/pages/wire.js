import {SearchResultsBar} from '../containers/searchResultsBar';

class WirePageWrapper {
    constructor() {
        this.searchResults = new SearchResultsBar();
    }

    showAdvancedSearchModal() {
        cy.get('[data-test-id="show-advanced-search-panel-btn"]').click();
    }

    showSaveTopicModal() {
        this.searchResults
            .getSearchResultElement('topics', '[data-test-id="save-topic-btn"]')
            .click();
    }
}

export const WirePage = new WirePageWrapper();
