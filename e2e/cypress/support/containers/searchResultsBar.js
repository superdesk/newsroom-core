
export class SearchResultsBar {
    toggleBar() {
        cy.get('[data-test-id="search-results-bar"] [data-test-id="toggle-search-bar"]').click();
    }

    getSearchResultTags(searchType) {
        return cy.get(`[data-test-id="search-results--${searchType}"]`);
    }

    getSearchResultElement(searchType, selector) {
        return cy.get(`[data-test-id="search-results--${searchType}"] ${selector}`);
    }

    expectAdvancedFields(enabledFields) {
        ['headline', 'slugline', 'body'].forEach((field) => {
            this
                .getSearchResultElement('advanced-fields', `[data-test-id="toggle-${field}-button"]`)
                .should(enabledFields.includes(field) ? 'have.class' : 'not.have.class', 'toggle-button--active');
        });
    }

    getAdvancedSearchKeywords(field) {
        const tagType = {
            and: 'success',
            any: 'info',
            exclude: 'alert',
        }[field];

        return this.getSearchResultElement('advanced-keywords', `[data-tag-type="${tagType}"]`);
    }

    expectAdvancedSearchKeywords(keywords) {
        Object.keys(keywords).forEach((field) => {
            keywords[field].forEach((keyword) => {
                this.getAdvancedSearchKeywords(field).contains(keyword);
            });
        });
    }
}
