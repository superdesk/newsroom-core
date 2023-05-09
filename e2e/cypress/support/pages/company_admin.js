
class CompanyAdminPageWrapper {
    getNavbar(additionalSelector) {
        let selector = '[data-test-id="company-admin--navbar"]';

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return cy.get(selector);
    }

    changeSubPage(name) {
        this.getNavbar(`[data-test-id="company-admin--${name}-btn"]`).click();
    }

    getUserList(additionalSelector) {
        let selector = '[data-test-id="company-admin--users-list"]';

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return cy.get(selector);
    }

    getUserListItems() {
        return this.getUserList('> tbody > tr');
    }

    getUserListItem(userId) {
        return this.getUserList(`[data-test-id="user-list-item--${userId}"]`);
    }

    getUserSeats(userId, section) {
        return this.getUserList(`[data-test-id="user-list-item--${userId}"] [data-test-id="user-seats--${section}"]`);
    }
}

export const CompanyAdminPage = new CompanyAdminPageWrapper();
