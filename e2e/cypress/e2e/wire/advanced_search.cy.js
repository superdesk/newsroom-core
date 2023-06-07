import {setup, addDefaultResources, addDefaultWireItems} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';
import {WirePage} from '../../support/pages/wire';
import {AdvancedSearchForm} from '../../support/forms/advancedSearch';
import {UserTopicForm} from '../../support/forms/userTopicForm';

describe('Wire - Advanced Search', function() {
    beforeEach(() => {
        setup();
        addDefaultResources();
        addDefaultWireItems();
        NewshubLayout.login('foo@bar.com', 'admin');
        NewshubLayout.getSidebarLink('wire').click();
    });

    it('can search', () => {
        WirePage.showAdvancedSearchModal();
        AdvancedSearchForm.type({
            all: 'Sydney Weather',
            'fields.headline': true,
            'fields.body_html': true,
        });
        AdvancedSearchForm.runSearch();
        const advancedSearchUrlParam = 'advanced=%7B%22all%22%3A%22Sydney+Weather%22%2C%22any%22%3A%22%22%2C%22' +
            'exclude%22%3A%22%22%2C%22fields%22%3A%5B%22headline%22%2C%22body_html%22%5D%7D';
        cy.url().should('include', advancedSearchUrlParam);

        cy.reload();
        cy.url().should('include', advancedSearchUrlParam);

        WirePage.showSaveTopicModal();
        UserTopicForm.type({name: 'Sydney Weather'});
        UserTopicForm.saveTopic(true);
        cy.url().should('not.include', advancedSearchUrlParam);
        UserTopicForm.getNewlyCreatedTopicId((topicId) => {
            cy.url().should('include', `topic=${topicId}`);
        });
        WirePage
            .getSearchResultTags()
            .contains('Sydney Weather');

        cy.reload();
        cy.url().should('not.include', advancedSearchUrlParam);
        UserTopicForm.getNewlyCreatedTopicId((topicId) => {
            cy.url().should('include', `topic=${topicId}`);
        });
        WirePage
            .getSearchResultTags()
            .contains('Sydney Weather');
    });
});
