
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
        cy.intercept('/api/users/*/topic_folders').as('getFolders');
        this.getFolderNameInput().type(name + '{enter}');
        cy.wait('@getFolders');
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
        return this.getBaseComponent(`[data-test-id="folder-card--${name}"]`);
    }

    dragTopicToFolder(topicName, folderName) {
        const dataTransfer = new DataTransfer();

        this.getTopicCard(topicName).trigger('dragstart', {dataTransfer});
        this.getFolderCard(folderName).trigger('drop', {dataTransfer});
    }
}

export const profileTopics = new ProfileTopicsWrapper();
