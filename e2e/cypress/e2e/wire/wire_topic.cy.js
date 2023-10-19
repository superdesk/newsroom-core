import {setup, addDefaultResources, addResources} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';
import {USERS} from '../../fixtures/users';
import {UserTopicForm} from '../../support/forms/userTopicForm';
import {COMPANIES} from '../../fixtures/companies';
import {profileTopics} from '../../support/pages/profile_topics';

const navigateToMyWireTopic = () => {
    cy.get('[data-test-id="sidenav-link-wire"]').click();
    cy.get('[data-test-id="toggle-filter-panel"]').click();
    cy.get('[data-test-id="filter-panel-tab--topics"]').click();
    cy.get('[data-test-id="edit-btn"]').click();
}

describe('Wire - Topic', function () {
    beforeEach(() => {
        setup();
        addDefaultResources();
    });

    it('Create a new folder in My Wire Topics', () => {
        addResources([
            {
                resource: 'topics',
                items: [
                    {
                        "_id": "672d3d26f27b4d52d8d5a37b", 
                        "query": "Topic 1",
                        "topic_type": "wire", 
                        "label": "Topic 1",
                        "user": USERS.none.admin._id, 
                    },
                ],
            },
        ]);
        NewshubLayout.login('admin@example.com', 'admin');
        navigateToMyWireTopic();

        profileTopics.createNewFolder('New Folder');

        // check if new folder appears in the list of My Wire Topics
        profileTopics.getFolderCard('New Folder').should('exist');

        // check if new folder appears in topic detail when editing My Wire Topic
        profileTopics.getTopicCardAction("Topic 1", "Edit").click();
        UserTopicForm
            .getFormGroup('folder', '[data-test-id="dropdown-btn"]')
            .contains('New Folder');
        cy.get('[data-test-id="profile-content-close"]').click();

        // create new topic to check if folder exist in select folder dropdown
        cy.get('[data-test-id="sidenav-link-wire"]').click();
        cy.get('[data-test-id="top-search-bar"]').click().type('New Topic');
        cy.get('[data-test-id="search-submit-button"]').click();
        cy.get('[data-test-id="save-topic-btn"]').click();
        UserTopicForm
            .getFormGroup('folder', '[data-test-id="dropdown-btn"]')
            .contains('New Folder');
    });

    it('Rename folder in My Wire Topics', () => {
        addResources([
            {
                resource: 'topic_folders',
                items: [
                    {
                        "_id": "652d2535b7e10e09ec704d6d",
                        "name": "Folder 1",
                        "section": "wire",
                        "user": USERS.none.admin._id
                    },
                ],
            },
        ]);
        NewshubLayout.login('admin@example.com', 'admin');
        navigateToMyWireTopic();

        // cancel rename
        profileTopics.getFolderAction("Folder 1", "Rename").click();
        cy.get('[data-test-id="folder-name--input"]').clear().type('Renamed Folder');
        cy.get('[data-test-id="create-folder--cancel-btn"]').click();
        // check if folder exist
        profileTopics.getFolderCard('Renamed Folder').should('not.exist');

        // save rename
        profileTopics.getFolderAction("Folder 1", "Rename").click();
        cy.get('[data-test-id="folder-name--input"]').clear().type('Renamed Folder');
        cy.get('[data-test-id="create-folder--submit-btn"]').click();
        // check if folder exist
        profileTopics.getFolderCard('Renamed Folder').should('exist');
    });

    it('Delete a folder with content in My Wire Topic', () => {
        addResources([
            {
                resource: 'topic_folders',
                items: [
                    {
                        "_id": "652d2535b7e10e09ec704d6d",
                        "name": "Folder 1",
                        "section": "wire",
                        "user": USERS.none.admin._id
                    },
                ],
            },
            {
                resource: 'topics',
                items: [
                    {
                        "_id": "672d3d26f27b4d56d8d5a27s",
                        "query": "Topic 1",
                        "topic_type": "wire",
                        "label": "Topic 1",
                        "user": USERS.none.admin._id, 
                        "folder": "652d2535b7e10e09ec704d6d",
                    }, 
                ],
            },
        ]);
        NewshubLayout.login('admin@example.com', 'admin');
        navigateToMyWireTopic();

        // delete folder with content
        profileTopics.getFolderAction("Folder 1", "Delete").click();

        // check that folder and content exist on DOM
        profileTopics.getFolderCard('Folder 1').should('not.exist');
        profileTopics.getTopicCard('Topic 1').should('not.exist');

        // refresh the page and check again
        cy.reload();
        cy.get('[data-test-id="edit-btn"]').click();
        profileTopics.getFolderCard('Folder 1').should('not.exist');
        profileTopics.getTopicCard('Topic 1').should('not.exist');
        cy.get('[data-test-id="profile-content-close"]').click();

        // create new topic to check if folder exist in select folder dropdown
        cy.get('[data-test-id="sidenav-link-wire"]').click();
        cy.get('[data-test-id="top-search-bar"]').click().type('My New Topic');
        cy.get('[data-test-id="search-submit-button"]').click();
        cy.get('[data-test-id="save-topic-btn"]').click();
        UserTopicForm
            .getFormGroup('folder', '[data-test-id="dropdown-btn"]')
            .contains('Folder 1').should('not.exist');
    });

    it('Create a new My Topic and save to folder', () => {
        addResources([
            {
                resource: 'topic_folders',
                items: [
                    {
                        "_id": "652d2535b7e10e09ec704d6d",
                        "name": "Folder 1",
                        "section": "wire",
                        "user": USERS.foobar.admin._id,
                    },
                    {
                        "_id": "672d3d26f27b4d52d8d5a87s",
                        "section": "wire",
                        "name": "company folder", 
                        "company": COMPANIES.foobar._id,
                    },
                ],
            },
        ]);
        NewshubLayout.login('foo@bar.com', 'admin');

        // create a My Topic
        cy.get('[data-test-id="sidenav-link-wire"]').click();
        cy.get('[data-test-id="top-search-bar"]').click().type('My Topic');
        cy.get('[data-test-id="search-submit-button"]').click();
        cy.get('[data-test-id="save-topic-btn"]').click();

        // check Share with my company checkbox
        cy.get('[data-test-id="field-is_global"] input').check();
        UserTopicForm
            .getFormGroup('folder', '[data-test-id="dropdown-btn"]').click()
            cy.get('[data-test-id="dropdown-item--Folder 1"]').should("not.exist");
            cy.get('[data-test-id="dropdown-item--company folder"]').should("exist");

        // uncheck Share with my company checkbox
        cy.get('[data-test-id="field-is_global"] input').uncheck();
        UserTopicForm
            .getFormGroup('folder', '[data-test-id="dropdown-btn"]').click()
            cy.get('[data-test-id="dropdown-item--Folder 1"]').should("exist");
            cy.get('[data-test-id="dropdown-item--company folder"]').should("not.exist");
        
        // save to folder
        cy.get('[data-test-id="dropdown-item--Folder 1"]').click();
        cy.get('[class="nh-button nh-button--primary"]').click();

        // check if topic exist in the Wire in appropriate folder on the left My Topics panel
        cy.get('[data-test-id="toggle-filter-panel"]').click();
        cy.get('[data-test-id="filter-panel-tab--topics"]').click();
        cy.get('[data-test-id="collapse-box-button"]').click();
        cy.get('[data-test-id="topic-list-item-My Topic"]').should('exist');

        // check if folder exist in appropriate folder in My Wire Topics
        cy.get('[data-test-id="edit-btn"]').click();
        profileTopics.getFolderCard("Folder 1").find('[data-test-id="simple-card-toggle-btn"]').click();
        profileTopics.getTopicCard('My Topic').should('exist');
    });

    it('Move My Topic to another folder', () => {
        addResources([
            {
                resource: 'topic_folders',
                items: [
                    {
                        "_id": "652d2535b7e10e09ec704d6d",
                        "name": "Folder 1",
                        "section": "wire",
                        "user": USERS.none.admin._id
                    },
                    {
                        "_id": "652d2535b7e10e09ec704d65",
                        "name": "Folder 2",
                        "section": "wire",
                        "user": USERS.none.admin._id
                    },
                ],
            },
            {
                resource: 'topics',
                items: [
                    {
                        "_id": "672d3d26f27b4d52d8d5a37b", 
                        "query": "Topic 1",
                        "topic_type": "wire", 
                        "label": "Topic 1",
                        "user": USERS.none.admin._id,
                        "folder": "652d2535b7e10e09ec704d6d"
                    },
                ],
            },
        ]);
        NewshubLayout.login('admin@admin.com', 'admin');
        navigateToMyWireTopic();

        profileTopics.getFolderCard("Folder 1").find('[data-test-id="simple-card-toggle-btn"]').click();

        // move topic to another folder with drag & drop
        profileTopics.dragTopicToFolder("Topic 1", "Folder 2");

        // check if topic exist in the Wire in appropriate folder on the left My Topics panel
        cy.get('[data-test-id="profile-content-close"]').click();
        cy.get('[data-test-id="collapse-box-button"]').click();
        cy.get('[data-test-id="topic-list-item-Topic 1"]').should('exist');

        // check if folder exist in appropriate folder in My Wire Topics
        cy.get('[data-test-id="edit-btn"]').click();
        profileTopics.getFolderCard("Folder 2").find('[data-test-id="simple-card-toggle-btn"]').click();
        profileTopics.getTopicCard('Topic 1').should('exist');
    });

    it('Remove My Topic from folder ', () => {
        addResources([
            {
                resource: 'topic_folders',
                items: [
                    {
                        "_id": "652d2535b7e10e09ec704d6d",
                        "name": "Folder 1",
                        "section": "wire",
                        "user": USERS.none.admin._id
                    },
                ],
            },
            {
                resource: 'topics',
                items: [
                    {
                        "_id": "672d3d26f27b4d52d8d5a37b",
                        "query": "Topic 1",
                        "topic_type": "wire", 
                        "label": "Topic 1",
                        "user": USERS.none.admin._id,
                        "folder": "652d2535b7e10e09ec704d6d"
                    },
                ],
            },
        ]);
        NewshubLayout.login('admin@admin.com', 'admin');
        navigateToMyWireTopic();

        // remove topic from folder
        profileTopics.getFolderCard("Folder 1").find('[data-test-id="simple-card-toggle-btn"]').click();
        cy.get('[data-test-id="topic-action--Remove from folder"]').click();

        // check that the topic appeared in root of My Wire Topics - is not in any folder
        cy.get('[data-test-id="topic-card--Topic 1"]').then(($el) => {
            const el = $el[0];
            expect(el.closest('[data-test-id="folder-card"]')).to.be.null;
        });

        // check that the topic appeared in the Wire in root on the left My Topics panel - is not in any folder
        cy.get('[data-test-id="profile-content-close"]').click();
        cy.get('[data-test-id="topic-list-item-Topic 1"]').then(($el) => {
            const el = $el[0];
            expect(el.closest('[data-test-id="folder-card"]')).to.be.null;
        });

    });
});
