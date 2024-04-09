import {setup, addDefaultResources} from '../../support/e2e';

// Pages & Containers
import {NewshubLayout} from '../../support/pages/layout';
import {CompanySettingsPage} from '../../support/pages/settings_company';
import {UserSettingsPage} from '../../support/pages/settings_users';
import {SettingsNav} from '../../support/containers/settingsNav';

// Forms
import {EditCompanyForm} from '../../support/forms/editCompany';
import {EditUserForm} from '../../support/forms/editUser';

// Fixtures
import {PRODUCTS} from '../../fixtures/products';

describe('CompanySettings', function() {
    beforeEach(() => {
        setup();
        addDefaultResources();
    });

    it('Can create new Company & User and assign sections and products', function() {
        // Login and navigate to Company settings page
        NewshubLayout.login('admin@example.com', 'admin');
        NewshubLayout.getSidebarLink('settings').click();
        SettingsNav.getNavLink('companies').click();

        // Create a new Company
        CompanySettingsPage.getNewCompanyButton().click();
        EditCompanyForm.type({
            name: 'My New Company',
            url: 'http://test.org',
            sd_subscriber_id: 'abcd123',
            account_manager: 'Foo Bar',
            phone: '1234 5678',
            contact_name: 'Foo',
            contact_email: 'foo@bar.org',
            country: 'other',
            expiry_date: '2030-12-31',
            is_enabled: true,
        });
        EditCompanyForm.save(true);

        // Open the newly created Company, and test its metadata is correct
        EditCompanyForm.getNewlyCreatedCompanyId((companyId) => {
            CompanySettingsPage.getCompanyListItem(companyId).click();
        });
        EditCompanyForm.expect({
            name: 'My New Company',
            url: 'http://test.org',
            sd_subscriber_id: 'abcd123',
            account_manager: 'Foo Bar',
            phone: '1234 5678',
            contact_name: 'Foo',
            contact_email: 'foo@bar.org',
            country: 'other',
            expiry_date: '2030-12-31',
            is_enabled: true,
        });

        // Change to Permissions tab, and test toggling permissions
        EditCompanyForm.changeTab('permissions');
        EditCompanyForm.permissions.type({
            archive_access: true,
            wire: true,
        });
        EditCompanyForm.permissions.toggleProducts({[PRODUCTS.wire.sports._id]: true});
        EditCompanyForm.permissions.typeProductSeats({[PRODUCTS.wire.sports._id]: '02'});
        EditCompanyForm.save();

        // Re-open the Company, and test the permissions are correct
        EditCompanyForm.getNewlyCreatedCompanyId((companyId) => {
            CompanySettingsPage.getCompanyListItem(companyId).click();
        });
        EditCompanyForm.changeTab('permissions');
        EditCompanyForm.permissions.expectProducts({[PRODUCTS.wire.sports._id]: true});
        EditCompanyForm.permissions.expectProductSeats({[PRODUCTS.wire.sports._id]: 2});

        // Navigate to the Users page and create a new user (assigned to newly created Company)
        SettingsNav.getNavLink('users').click();
        UserSettingsPage.getNewUserButton().click();
        EditUserForm.openAllToggleBoxes();
        EditUserForm.type({
            first_name: 'Null',
            last_name: 'Abore',
            email: 'nullabore@bar.org',
            phone: '0123',
            mobile: '4567',
            role: 'Reviewer',
            expiry_alert: true,
            manage_company_topics: true,
        });
        EditCompanyForm.getNewlyCreatedCompanyId((companyId) => {
            EditUserForm.type({company: companyId});
        });

        // Make sure Wire section is available, and defaulted to true
        EditUserForm.expectSections({wire: true});
        EditUserForm.expectSectionsMissing(['agenda']);

        // Enable Wire section for this User
        EditUserForm.expectProducts({wire: {[PRODUCTS.wire.sports._id]: false}});
        EditUserForm.typeProducts({wire: {[PRODUCTS.wire.sports._id]: true}});
        EditUserForm.expectProductsMissing({
            wire: [PRODUCTS.wire.all._id],
            agenda: [PRODUCTS.agenda.sports._id],
        });
        EditUserForm.save(true);

        // Check the user has the correct metadata and permissions
        EditUserForm.getNewlyCreatedUserId((userId) => {
            UserSettingsPage.getUserListItem(userId).click();
        });
        EditUserForm.openAllToggleBoxes();
        EditUserForm.expect({
            first_name: 'Null',
            last_name: 'Abore',
            email: 'nullabore@bar.org',
            phone: '0123',
            mobile: '4567',
            role: 'Reviewer',
            expiry_alert: true,
            manage_company_topics: true,
        });

        EditUserForm.expectProducts({wire: {[PRODUCTS.wire.sports._id]: true}});
        EditUserForm.expectProductsMissing({
            wire: [PRODUCTS.wire.all._id],
            agenda: [PRODUCTS.agenda.sports._id],
        });
    });

    it('TGA-86: User section permissions are not lost when saving other metadata', function() {
        // Login and navigate to Company settings page
        NewshubLayout.login('admin@example.com', 'admin');
        NewshubLayout.getSidebarLink('settings').click();
        SettingsNav.getNavLink('companies').click();

        // Create a new Company
        CompanySettingsPage.getNewCompanyButton().click();
        EditCompanyForm.type({name: 'My New Company'});
        EditCompanyForm.save(true);

        // Open the newly created Company, and set permissions
        EditCompanyForm.getNewlyCreatedCompanyId((companyId) => {
            CompanySettingsPage.getCompanyListItem(companyId).click();
        });
        EditCompanyForm.changeTab('permissions');
        EditCompanyForm.permissions.type({
            wire: true,
            agenda: true,
        });
        EditCompanyForm.permissions.toggleProducts({
            [PRODUCTS.wire.sports._id]: true,
            [PRODUCTS.agenda.sports._id]: true,
        });
        EditCompanyForm.save();

        // Navigate to the Users page and create a new user (assigned to newly created Company)
        SettingsNav.getNavLink('users').click();
        UserSettingsPage.getNewUserButton().click();
        EditUserForm.openAllToggleBoxes();
        EditUserForm.type({
            first_name: 'Null',
            last_name: 'Abore',
            email: 'nullabore@bar.org',
        });
        EditCompanyForm.getNewlyCreatedCompanyId((companyId) => {
            EditUserForm.type({company: companyId});
        });

        // Make sure permissions are correct, and save
        EditUserForm.expectSections({wire: true, agenda: true});
        EditUserForm.expectProducts({
            wire: {[PRODUCTS.wire.sports._id]: true},
            agenda: {[PRODUCTS.agenda.sports._id]: true},
        });
        EditUserForm.save(true);

        // Make changes other than permissions to the user, and save
        cy.reload();
        EditUserForm.getNewlyCreatedUserId((userId) => {
            UserSettingsPage.getUserListItem(userId).click();
        });
        EditUserForm.type({role: 'Tester'});
        EditUserForm.save();

        // Make sure this user has not lost their section permissions
        cy.reload();
        EditUserForm.getNewlyCreatedUserId((userId) => {
            UserSettingsPage.getUserListItem(userId).click();
        });
        EditUserForm.openAllToggleBoxes();
        EditUserForm.expectSections({wire: true, agenda: true});
        EditUserForm.expectProducts({
            wire: {[PRODUCTS.wire.sports._id]: true},
            agenda: {[PRODUCTS.agenda.sports._id]: true},
        });
    });

    it('Section permissions use parent Company until changed on the user level', function() {
        // Login and navigate to Company settings page
        NewshubLayout.login('admin@example.com', 'admin');
        NewshubLayout.getSidebarLink('settings').click();
        SettingsNav.getNavLink('companies').click();

        // Create a new Company
        CompanySettingsPage.getNewCompanyButton().click();
        EditCompanyForm.type({name: 'My New Company'});
        EditCompanyForm.save(true);

        // Open the newly created Company, and test its metadata is correct
        EditCompanyForm.getNewlyCreatedCompanyId((companyId) => {
            CompanySettingsPage.getCompanyListItem(companyId).click();
        });

        // Change to Permissions tab, and test toggling permissions
        EditCompanyForm.changeTab('permissions');
        EditCompanyForm.permissions.type({
            wire: true,
            agenda: true,
        });
        EditCompanyForm.permissions.toggleProducts({
            [PRODUCTS.wire.sports._id]: true,
            [PRODUCTS.agenda.sports._id]: true,
        });
        EditCompanyForm.save();

        // Navigate to the Users page and create a new user (assigned to newly created Company)
        SettingsNav.getNavLink('users').click();
        UserSettingsPage.getNewUserButton().click();
        EditUserForm.openAllToggleBoxes();

        EditUserForm.type({
            first_name: 'Null',
            last_name: 'Abore',
            email: 'nullabore@bar.org',
        });
        EditCompanyForm.getNewlyCreatedCompanyId((companyId) => {
            EditUserForm.type({company: companyId});
        });

        EditUserForm.expectSections({wire: true, agenda: true});
        EditUserForm.expectProducts({
            wire: {[PRODUCTS.wire.sports._id]: true},
            agenda: {[PRODUCTS.agenda.sports._id]: true},
        });
        EditUserForm.save(true);

        // Check the user has the correct permissions
        EditUserForm.getNewlyCreatedUserId((userId) => {
            UserSettingsPage.getUserListItem(userId).click();
        });
        EditUserForm.openAllToggleBoxes();
        EditUserForm.expectSections({wire: true, agenda: true});
        EditUserForm.expectProducts({
            wire: {[PRODUCTS.wire.sports._id]: true},
            agenda: {[PRODUCTS.agenda.sports._id]: true},
        });

        // Navigate back to the Company page and disable the Agenda section
        SettingsNav.getNavLink('companies').click();
        EditCompanyForm.getNewlyCreatedCompanyId((companyId) => {
            CompanySettingsPage.getCompanyListItem(companyId).click();
        });
        EditCompanyForm.changeTab('permissions');
        EditCompanyForm.permissions.type({agenda: false});
        EditCompanyForm.save();

        // Navigate back to the users page and make sure Agenda is not shown
        SettingsNav.getNavLink('users').click();
        EditUserForm.getNewlyCreatedUserId((userId) => {
            UserSettingsPage.getUserListItem(userId).click();
        });
        EditUserForm.openAllToggleBoxes();
        EditUserForm.expectSectionsMissing(['agenda']);

        // Navigate back to the Company page and re-enable the Agenda section
        SettingsNav.getNavLink('companies').click();
        EditCompanyForm.getNewlyCreatedCompanyId((companyId) => {
            CompanySettingsPage.getCompanyListItem(companyId).click();
        });
        EditCompanyForm.changeTab('permissions');
        EditCompanyForm.permissions.type({agenda: true});
        EditCompanyForm.save();

        // Navigate back to the users page and make sure Agenda is shown again, and enabled
        SettingsNav.getNavLink('users').click();
        EditUserForm.getNewlyCreatedUserId((userId) => {
            UserSettingsPage.getUserListItem(userId).click();
        });
        EditUserForm.openAllToggleBoxes();
        EditUserForm.expectSections({wire: true, agenda: true});
    });
});
