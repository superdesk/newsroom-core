
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
}

export const CompanyAdminPage = new CompanyAdminPageWrapper();
