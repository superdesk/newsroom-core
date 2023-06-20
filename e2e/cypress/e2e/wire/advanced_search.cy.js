import {setup, addDefaultResources, addDefaultWireItems} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';
import {WirePage} from '../../support/pages/wire';
import {AdvancedSearchForm} from '../../support/forms/advancedSearch';
import {UserTopicForm} from '../../support/forms/userTopicForm';

const encodeSearchParams = (params) => {
    const p = new URLSearchParams();

    p.set('advanced', JSON.stringify(params));

    return p.toString();
};

describe('Wire - Advanced Search', function() {
    beforeEach(() => {
        setup();
        addDefaultResources();
        addDefaultWireItems();
        NewshubLayout.login('foo@bar.com', 'admin');
        NewshubLayout.getSidebarLink('wire').click();
    });

    it('can search', () => {
        function expectSearchResultBarTags() {
            WirePage.searchResults.expectAdvancedFields(['headline', 'body']);
            WirePage.searchResults.expectAdvancedSearchKeywords({
                and: ['Weather'],
                any: ['Sydney', 'Prague', 'Belgrade'],
                exclude: ['London'],
            });
        }

        WirePage.showAdvancedSearchModal();
        AdvancedSearchForm.type({
            all: 'Weather',
            any: 'Sydney Prague Belgrade',
            exclude: 'London',
            'fields.slugline': false,
        });
        AdvancedSearchForm.runSearch();
        const advancedSearchUrlParam = encodeSearchParams({
            all: 'Weather',
            any: 'Sydney Prague Belgrade',
            exclude: 'London',
            fields: ['headline', 'body_html'],
        });
        cy.url().should('include', advancedSearchUrlParam);
        WirePage.searchResults.toggleBar();
        expectSearchResultBarTags();

        cy.reload();
        cy.url().should('include', advancedSearchUrlParam);
        WirePage.searchResults.toggleBar();
        expectSearchResultBarTags();

        WirePage.showSaveTopicModal();
        UserTopicForm.type({name: 'Sofab Weather'});
        UserTopicForm.saveTopic(true);
        cy.url().should('not.include', advancedSearchUrlParam);
        UserTopicForm.getNewlyCreatedTopicId((topicId) => {
            cy.url().should('include', `topic=${topicId}`);
        });
        WirePage.searchResults
            .getSearchResultTags('topics')
            .contains('Sofab Weather');
        expectSearchResultBarTags();

        cy.reload();
        cy.url().should('not.include', advancedSearchUrlParam);
        UserTopicForm.getNewlyCreatedTopicId((topicId) => {
            cy.url().should('include', `topic=${topicId}`);
        });
        WirePage.searchResults.toggleBar();
        WirePage.searchResults
            .getSearchResultTags('topics')
            .contains('Sofab Weather');
        expectSearchResultBarTags();

        // Remove one tag, and make sure the update/create buttons appear
        WirePage.searchResults
            .getSearchResultElement('topics', '[data-test-id="update-topic-btn"]')
            .should('not.exist');
        WirePage.searchResults
            .getSearchResultElement('topics', '[data-test-id="save-topic-btn"]')
            .should('not.exist');

        WirePage.searchResults.getAdvancedSearchKeywords('and')
            .should('have.length', 2);
        WirePage.searchResults
            .getSearchResultElement('advanced-keywords', '[data-test-id="remove-tag-button"]')
            .first()
            .click();
        WirePage.searchResults.getAdvancedSearchKeywords('and')
            .should('have.length', 0);
        WirePage.searchResults
            .getSearchResultElement('topics', '[data-test-id="update-topic-btn"]')
            .should('exist');
        WirePage.searchResults
            .getSearchResultElement('topics', '[data-test-id="save-topic-btn"]')
            .should('exist');

        // Remove the "My Topic" tag
        WirePage.searchResults
            .getSearchResultElement('topics', '[data-test-id="remove-tag-button"]')
            .click();
        WirePage.searchResults.expectAdvancedFields(['headline', 'body']);
        WirePage.searchResults.expectAdvancedSearchKeywords({
            any: ['Sydney', 'Prague', 'Belgrade'],
            exclude: ['London'],
        });
        WirePage.searchResults
            .getSearchResultElement('topics', '[data-test-id="tags-topics--topic"]')
            .should('have.length', 0);
        WirePage.searchResults.getAdvancedSearchKeywords('and')
            .should('have.length', 0);
    });
});
