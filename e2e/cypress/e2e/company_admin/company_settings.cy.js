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
        NewshubLayout.login('admin@nistrator.org', 'admin');
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
            country: 'Aruba',
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
            country: 'Aruba',
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

        // Make sure Wire section is available, and defaulted to false
        EditUserForm.expectSections({wire: false});
        EditUserForm.expectSectionsMissing(['agenda']);
        EditUserForm.expectProductsMissing({
            wire: [PRODUCTS.wire.all._id, PRODUCTS.wire.sports._id],
            agenda: [PRODUCTS.agenda.sports._id],
        });

        // Enable Wire section for this User
        EditUserForm.typeSections({wire: true});
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
        EditUserForm.expectSections({wire: true});
        EditUserForm.expectSectionsMissing(['agenda']);
        EditUserForm.expectProducts({wire: {[PRODUCTS.wire.sports._id]: true}});
        EditUserForm.expectProductsMissing({
            wire: [PRODUCTS.wire.all._id],
            agenda: [PRODUCTS.agenda.sports._id],
        });
    });
});
