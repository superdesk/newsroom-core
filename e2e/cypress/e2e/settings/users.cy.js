import {setup, addDefaultResources} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';
import {SettingsNav} from '../../support/containers/settingsNav';
import {UserSettingsPage} from '../../support/pages/settings_users';
import {CompanySettingsPage} from '../../support/pages/settings_company';
import {EditUserForm} from '../../support/forms/editUser';
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

    it('can use Azure as auth provider for company', () => {
        UserSettingsPage.getUserListItem(USERS.foobar.admin._id).click();
        cy.get('[data-test-id="reset-password-btn"]').should('exist');

        SettingsNav.getNavLink('companies').click();
        CompanySettingsPage.getCompanyListItem(COMPANIES.foobar._id).click();
        cy.get('[data-test-id="field-auth_domains"]').should('not.exist');

        cy.get('[data-test-id="field-auth_provider-select"]').select('azure');
        cy.get('[data-test-id="field-auth_domains"]').should('exist');

        cy.get('[data-test-id="save-btn"]').click();

        SettingsNav.getNavLink('users').click();
        UserSettingsPage.getUserListItem(USERS.foobar.admin._id).click();
        cy.get('[data-test-id="reset-password-btn"]').should('not.exist');
    });

    it('keeps selected Finnish language when creating and updating a user', () => {
        UserSettingsPage.getNewUserButton().click();

        EditUserForm.type({
            first_name: 'Locale',
            last_name: 'Regression',
            email: 'locale.regression@bar.org',
            company: COMPANIES.foobar._id,
        });
        cy.get('[data-test-id="field-locale-select"] option').then(($options) => {
            const englishOption = [...$options].find((option) => /english/i.test(option.text));
            const finnishOption = [...$options].find((option) => /suomi|finnish|fi/i.test(option.text));

            expect(englishOption, 'English locale option should exist').to.exist;
            expect(finnishOption, 'Finnish locale option should exist').to.exist;
            expect(finnishOption.value, 'Finnish locale value should differ from English').to.not.eq(englishOption.value);

            cy.wrap(finnishOption.value).as('finnishLocaleValue');
            cy.get('[data-test-id="field-locale-select"]').select(finnishOption.value);
        });
        EditUserForm.save(true);

        EditUserForm
            .getFormElement()
            .should('not.exist');

        EditUserForm.getNewlyCreatedUserId((userId) => {
            UserSettingsPage.getUserListItem(userId).click();
        });

        cy.get('@finnishLocaleValue').then((localeValue) => {
            EditUserForm.expect({locale: localeValue});
        });

        EditUserForm.save();

        EditUserForm
            .getFormElement()
            .should('not.exist');

        EditUserForm.getNewlyCreatedUserId((userId) => {
            UserSettingsPage.getUserListItem(userId).click();
        });

        cy.get('@finnishLocaleValue').then((localeValue) => {
            EditUserForm.expect({locale: localeValue});
        });
    });
});