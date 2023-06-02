
class UserSettingsPageWrapper {
    getUserList(additionalSelector) {
        let selector = '[data-test-id="user-list"]';

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return cy.get(selector);
    }

    getUserListItem(userId) {
        return this.getUserList(`[data-test-id="user-list-item--${userId}"]`);
    }

    getNewUserButton() {
        return cy.get('[data-test-id="new-item-btn"]');
    }
}

export const UserSettingsPage = new UserSettingsPageWrapper();
