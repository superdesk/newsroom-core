import {setup, addDefaultResources} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';
import {SettingsNav} from '../../support/containers/settingsNav';
import {UserSettingsPage} from '../../support/pages/settings_users';
import {CompanySettingsPage} from '../../support/pages/settings_company';
import {USERS} from '../../fixtures/users';
import {COMPANIES} from '../../fixtures/companies';

describe('Settings - Users', function () {
    beforeEach(() => {
        setup();
        addDefaultResources();
        NewshubLayout.login('admin@example.com', 'admin');
        NewshubLayout.getSidebarLink('settings').click();
        SettingsNav.getNavLink('users').click();
    });

    it('can impersonate a user', () => {
        UserSettingsPage
            .getUserListItem(USERS.foobar.monkey._id)
            .click();

        NewshubLayout
            .getAvatar()
            .should('contain.text', 'AN');

        UserSettingsPage
            .getPreview()
            .should('contain.text', 'Impersonate User');

        cy.get('[data-test-id="impersonate-user-btn"]').click();

        cy.url().should('eq', 'http://localhost:5050/');

        NewshubLayout
            .getAvatar()
            .should('contain.text', 'MM');

        cy.get('[data-test-id="impersonate-user-info"]')
            .should('include.text', 'Impersonating')
            .should('include.text', 'Monkey Mania');

        cy.get('[data-test-id="impersonate-stop-btn"]')
            .click();

        cy.url().should('eq', 'http://localhost:5050/settings/users');

        cy.get('[data-test-id="impersonate-user-info"]')
            .should('not.exist');

        UserSettingsPage
            .getUserListItem(USERS.none.admin._id)
            .click();

        UserSettingsPage
            .getPreview()
            .should('not.contain', 'Impersonate User');
    });

    it('can hide reset password for Azure auth company', () => {
        SettingsNav.getNavLink('users').click();
        UserSettingsPage.getUserListItem(USERS.foobar.admin._id).click();
        cy.get('[data-test-id="reset-password-btn"]').should('exist');

        SettingsNav.getNavLink('companies').click();
        CompanySettingsPage.getCompanyListItem(COMPANIES.foobar._id).click();
        cy.get('[data-test-id="field-auth_provider-select"]').select('azure');
        cy.get('[data-test-id="save-btn"]').click();

        SettingsNav.getNavLink('users').click();
        UserSettingsPage.getUserListItem(USERS.foobar.admin._id).click();
        cy.get('[data-test-id="reset-password-btn"]').should('not.exist');
    });
});