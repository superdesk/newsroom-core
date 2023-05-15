
class CompanySettingsPageWrapper {
    getCompanyList(additionalSelector) {
        let selector = '[data-test-id="company-list"]';

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return cy.get(selector);
    }

    getCompanyListItems() {
        return this.getCompanyList('> tbody > tr');
    }

    getCompanyListItem(companyId) {
        return this.getCompanyList(`[data-test-id="company-list-item--${companyId}"]`);
    }

    getNewCompanyButton() {
        return cy.get('[data-test-id="new-item-btn"]');
    }
}

export const CompanySettingsPage = new CompanySettingsPageWrapper();
