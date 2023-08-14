import {SearchResultsBar} from '../containers/searchResultsBar';
import {FilterPanelContainer} from '../containers/filterPanel';

class WirePageWrapper {
    constructor() {
        this.searchResults = new SearchResultsBar();
        this.filterPanel = new FilterPanelContainer();
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
}

export const WirePage = new WirePageWrapper();
