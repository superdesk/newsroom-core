
class NewshubSettingsPageWrapper {
    getList(additionalSelector) {
        let selector = '[data-test-id="company-list"]';

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return cy.get(selector);
    }

    getListItems() {
        return this.getList('> tbody > tr');
    }
}

export const NewshubSettingsPage = new NewshubSettingsPageWrapper();
