
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

    expectFilterTags(filterParams) {
        Object.keys(filterParams).forEach((group) => {
            filterParams[group].forEach((filterValue) => {
                this.getSearchResultElement('filters', `[data-test-id="tags-filters--${group}"]`)
                    .contains(filterValue);
            });
        });
    }

    expectSearchResults(params) {
        if (params.advanced != null) {
            if (params.advanced.fields != null) {
                this.expectAdvancedFields(params.advanced.fields);
            }
            if (params.advanced.keywords != null) {
                this.expectAdvancedSearchKeywords(params.advanced.keywords);
            }
        }
        if (params.query != null) {
            this.getSearchResultElement('query', '[data-test-id="query-value"]')
                .contains(params.query);
        }
        if (params.topics != null) {
            params.topics.forEach((topicName) => {
                this.getSearchResultElement('topics', '[data-test-id="tags-topic"]')
                    .contains(topicName);
            });
        }
        if (params.myTopic != null) {
            this.getSearchResultElement('topics', '[data-test-id="tags-topics--my-topic"]')
                .contains(params.myTopic);
        }
        if (params.filters != null) {
            this.expectFilterTags(params.filters);
        }
    }
}
