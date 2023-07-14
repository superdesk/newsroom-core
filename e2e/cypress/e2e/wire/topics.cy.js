import {setup, addDefaultResources, addAllWireItems} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';
import {WirePage} from '../../support/pages/wire';
import {profileTopics} from '../../support/pages/profile_topics';

import {AdvancedSearchForm} from '../../support/forms/advancedSearch';
import {UserTopicForm} from '../../support/forms/userTopicForm';

describe('Wire - Topics', function () {
    beforeEach(() => {
        setup();
        addDefaultResources();
        addAllWireItems();
        NewshubLayout.login('foo@bar.com', 'admin');
        NewshubLayout.getSidebarLink('wire').click();
    });

    it('can save a new topic', () => {
        function expectSearchResultsBarTags(includeMyTopic, fromTopicForm = false) {
            const expectedSearchResults = {
                advanced: {
                    fields: ['headline', 'body'],
                    keywords: {
                        and: ['Weather'],
                        any: ['Sydney', 'Prague', 'Belgrade'],
                        exclude: ['London'],
                    },
                },
                query: 'Today',
                topics: ['All wire'],
                filters: {
                    Category: ['Traffic', 'Weather'],
                    Subject: ['archaeology'],
                    'Content Type': ['Article (news)'],
                    'News Value': ['3'],
                    Place: ['New South Wales', 'Queensland'],
                    'created-from': ['01/06/2023'],
                    'created-to': ['30/06/2023'],
                },
            }

            if (includeMyTopic) {
                expectedSearchResults.myTopic = 'Sofab Weather';
            }

            fromTopicForm !== true ?
                WirePage.searchResults.expectSearchResults(expectedSearchResults) :
                UserTopicForm.searchParams.expectSearchResults(expectedSearchResults);
        }

        // Select the 'All Wire' global topic
        WirePage.filterPanel.toggleFilterPanel();
        WirePage.filterPanel.getTopicButton('all wire').click();

        // Enter in 'Today' in the top search bar
        WirePage.getTopSearchBarInput().type('Today{enter}');

        // Add some filter params
        WirePage.filterPanel.selectTab('filters');
        WirePage.filterPanel.type({
            category: ['Traffic', 'Weather'],
            subject: ['archaeology'],
            'content type': ['Article (news)'],
            'news value': ['3'],
            place: ['New South Wales', 'Queensland'],
        });
        WirePage.filterPanel.getNavGroupInput('published', 'created-from')
            .type('2023-06-01');
        WirePage.filterPanel.getNavGroupInput('published', 'created-to')
            .type('2023-06-30');
        WirePage.filterPanel.runSearch();

        // Add advanced search params
        WirePage.showAdvancedSearchModal();
        AdvancedSearchForm.type({
            all: 'Weather',
            any: 'Sydney Prague Belgrade',
            exclude: 'London',
            'fields.slugline': false,
        });
        AdvancedSearchForm.runSearch();

        // Open the search results bar, and make sure all search params are applied
        WirePage.searchResults.toggleBar();
        expectSearchResultsBarTags(false);

        // Reload the page and make sure all search params are still applied
        cy.reload();
        WirePage.searchResults.toggleBar();
        expectSearchResultsBarTags(false);

        // Save the new Topic
        WirePage.showSaveTopicModal();
        UserTopicForm.type({name: 'Sofab Weather'});
        UserTopicForm.toggleFormGroup('params');
        expectSearchResultsBarTags(false, true);
        UserTopicForm.saveTopic();
        expectSearchResultsBarTags(true);

        // Now edit the 'My Topic', and add it to a folder
        WirePage.filterPanel.selectTab('topics');
        WirePage.filterPanel.getCurrentPanel('[data-test-id="edit-btn"]').click();
        profileTopics.createNewFolder("Weather");
        profileTopics.createNewFolder("Traffic");
        profileTopics.dragTopicToFolder('Sofab Weather', 'Weather');
        profileTopics
            .getTopicCardAction('Sofab Weather', 'Remove from folder')
            .should('exist');

        // Open the Topic for editing, and check the search params etc
        profileTopics.getTopicCardAction('Sofab Weather', 'Edit').click();
        UserTopicForm.toggleFormGroup('folder');
        UserTopicForm
            .getFormGroup('folder', '[data-test-id="dropdown-btn"]')
            .contains('Weather');
        UserTopicForm
            .getFormGroup('folder', '[data-test-id="dropdown-btn"]')
            .click();
        UserTopicForm
            .getFormGroup('folder', '[data-test-id="dropdown-item--Traffic"]')
            .click();
        UserTopicForm.toggleFormGroup('params');
        expectSearchResultsBarTags(false, true);
        UserTopicForm.saveTopic();
    });
});
