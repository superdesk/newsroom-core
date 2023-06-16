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
        WirePage.showAdvancedSearchModal();
        AdvancedSearchForm.type({
            all: 'Sydney Weather',
            'fields.slugline': false,
        });
        AdvancedSearchForm.runSearch();
        const advancedSearchUrlParam = encodeSearchParams({all: 'Sydney Weather', any: '', exclude: '', fields: ['headline', 'body_html']});
        cy.url().should('include', advancedSearchUrlParam);

        cy.reload();
        cy.url().should('include', advancedSearchUrlParam);

        WirePage.toggleSearchResultsBar();
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
        WirePage.toggleSearchResultsBar();
        WirePage
            .getSearchResultTags()
            .contains('Sydney Weather');
    });
});
