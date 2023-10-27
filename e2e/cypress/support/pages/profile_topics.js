import {dragAndDrop} from '../dnd/utils';

class ProfileTopicsWrapper {
    getBaseComponent(additionalSelector) {
        let selector = '[data-test-id="profile-container"]';

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return cy.get(selector);
    }

    getCreateFolderButton() {
        return this.getBaseComponent('[data-test-id="create-folder-btn"]');
    }

    getFolderNameInput() {
        return this.getBaseComponent('[data-test-id="folder-name--input"]');
    }

    createNewFolder(name) {
        this.getCreateFolderButton().click();
        this.getFolderNameInput().type(name + '{enter}');
        cy.get(`[data-test-id="folder-card"][data-test-value="${name}"]`).should('be.visible');
    }

    getTopicCard(name, additionalSelector) {
        let selector = `[data-test-id="topic-card--${name}"]`;

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return this.getBaseComponent(selector);
    }

    getTopicCardAction(topicName, actionName) {
        return this.getTopicCard(topicName, `[data-test-id="topic-action--${actionName}"]`);
    }

    getFolderCard(name) {
        return this.getBaseComponent(`[data-test-id="folder-card"][data-test-value="${name}"]`);
    }

    getFolderAction(name, actionName) {
        cy.get(`[data-test-id="folder-card"][data-test-value="${name}"] [data-test-id="menu"]`).click();
        return cy.get(`[data-test-id="action-folder"][data-test-value="${actionName}"]`);
    }

    dragTopicToFolder(topicName, folderName) {
        dragAndDrop(
            this.getTopicCard(topicName),
            this.getFolderCard(folderName),
        );
    }
}

export const profileTopics = new ProfileTopicsWrapper();
