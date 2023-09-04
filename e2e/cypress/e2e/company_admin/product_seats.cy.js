import {setup, addDefaultResources} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';
import {CompanyAdminPage} from '../../support/pages/company_admin';
import {EditUserForm} from '../../support/forms/editUser';

import {PRODUCTS} from '../../fixtures/products';
import {COMPANIES} from '../../fixtures/companies';
import {USERS} from '../../fixtures/users';

describe('CompanyAdmin - Product Seats', function () {
    beforeEach(() => {
        setup();
        addDefaultResources();
    });

    it('CopmanyAdmin can manage their user product permissions', () => {
        // Login and navigate to CompanyAdmin page
        NewshubLayout.login('foo@bar.com', 'admin');
        NewshubLayout.getSidebarLink('company_admin').click();

        // Switch to the Users page, and make sure we have 2 users there
        CompanyAdminPage.changeSubPage('users');
        CompanyAdminPage
            .getUserListItems()
            .should('have.length', 2);
        CompanyAdminPage
            .getUserListItem(USERS.foobar.monkey._id)
            .click();

        // Make sure the form has all the appropriate values & permissions
        EditUserForm.openAllToggleBoxes();
        EditUserForm.expect({
            first_name: USERS.foobar.monkey.first_name,
            last_name: USERS.foobar.monkey.last_name,
            email: USERS.foobar.monkey.email,
            phone: '',
            mobile: '',
            role: '',
            user_type: USERS.foobar.monkey.user_type,
            company_read_only: COMPANIES.foobar.name,
            locale: '',
            expiry_alert: false,
            manage_company_topics: false,
        });
        EditUserForm.expectSections({
            wire: true,
            agenda: true,
        });
        EditUserForm.expectProducts({
            wire: {
                [PRODUCTS.wire.all._id]: false,
                [PRODUCTS.wire.sports._id]: true,
            },
            agenda: {
                [PRODUCTS.agenda.sports._id]: true,
            },
        });

        // Change some values & permissions
        EditUserForm.type({
            first_name: 'Monkey 2',
            last_name: 'Mania 3',
            email: 'monkey.mania_4@bar.com',
            phone: '1234',
            mobile: '5678',
            role: 'test user',
            expiry_alert: true,
        });
        EditUserForm.typeSections({agenda: false});
        EditUserForm.typeProducts({wire: {
            [PRODUCTS.wire.all._id]: true,
            [PRODUCTS.wire.sports._id]: false,
        }});

        function expectUpdatedUser() {
            EditUserForm.expect({
                first_name: 'Monkey 2',
                last_name: 'Mania 3',
                email: 'monkey.mania_4@bar.com',
                phone: '1234',
                mobile: '5678',
                role: 'test user',
                user_type: 'public',
                company_read_only: 'Foo Bar & Co',
                locale: '',
                expiry_alert: true,
                manage_company_topics: false,
            });
            EditUserForm.expectSections({
                wire: true,
                agenda: false,
            });
            EditUserForm.expectProducts({
                wire: {
                    [PRODUCTS.wire.all._id]: true,
                    [PRODUCTS.wire.sports._id]: false,
                },
            });
        }

        // Make sure the form has all the appropriate values & permissions
        expectUpdatedUser();

        // Save the user, re-open it, and make sure the form has all the appropriate values & permissions
        EditUserForm.save();
        EditUserForm
            .getFormElement()
            .should('not.exist');
        CompanyAdminPage
            .getUserListItem(USERS.foobar.monkey._id)
            .should('contain.text', 'Monkey 2');
        CompanyAdminPage
            .getUserListItem(USERS.foobar.monkey._id)
            .click();
        EditUserForm
            .getFormElement()
            .should('be.visible');
        EditUserForm.openAllToggleBoxes();
        expectUpdatedUser();

        // Reload the page, re-open it, and make sure the form has all the appropriate values & permissions
        cy.reload();
        CompanyAdminPage.changeSubPage('users');
        CompanyAdminPage
            .getUserListItem(USERS.foobar.monkey._id)
            .click();
        EditUserForm.openAllToggleBoxes();
        expectUpdatedUser();
    });

    it('CompanyAdmin can remove all products from a user', () => {
        // Login and navigate to CompanyAdmin page
        NewshubLayout.login('foo@bar.com', 'admin');
        NewshubLayout.getSidebarLink('company_admin').click();

        // Switch to the Users page, and open User 'Monkey Mania' for editing
        CompanyAdminPage.changeSubPage('users');
        CompanyAdminPage
            .getUserListItem(USERS.foobar.monkey._id)
            .click();

        // Make sure the form has all the appropriate values & permissions
        EditUserForm.openAllToggleBoxes();
        EditUserForm.expectProducts({
            wire: {
                [PRODUCTS.wire.all._id]: false,
                [PRODUCTS.wire.sports._id]: true,
            },
            agenda: {
                [PRODUCTS.agenda.sports._id]: true,
            },
        });

        // Remove all product permissions for the user
        EditUserForm.typeProducts({
            wire: {
                [PRODUCTS.wire.sports._id]: false,
            },
            agenda: {
                [PRODUCTS.agenda.sports._id]: false,
            },
        });

        // Make sure the form has all the appropriate product permissions
        EditUserForm.expectProducts({
            wire: {
                [PRODUCTS.wire.all._id]: false,
                [PRODUCTS.wire.sports._id]: false,
            },
            agenda: {
                [PRODUCTS.agenda.sports._id]: false,
            },
        });

        // Save the user, re-open it, and make sure the form has all the appropriate product permissions
        EditUserForm.save();
        EditUserForm
            .getFormElement()
            .should('not.exist');
        CompanyAdminPage
            .getUserSeats(USERS.foobar.monkey._id, 'wire')
            .should('contain.text', '0');
        CompanyAdminPage
            .getUserSeats(USERS.foobar.monkey._id, 'agenda')
            .should('contain.text', '0');
        CompanyAdminPage
            .getUserListItem(USERS.foobar.monkey._id)
            .click();
        EditUserForm
            .getFormElement()
            .should('be.visible');
        EditUserForm.openAllToggleBoxes();
        EditUserForm.expectProducts({
            wire: {
                [PRODUCTS.wire.all._id]: false,
                [PRODUCTS.wire.sports._id]: false,
            },
            agenda: {
                [PRODUCTS.agenda.sports._id]: false,
            },
        });

        // Reload the page, re-open it, and make sure the form has all the appropriate product permissions
        cy.reload();
        CompanyAdminPage.changeSubPage('users');
        CompanyAdminPage
            .getUserListItem(USERS.foobar.monkey._id)
            .click();
        EditUserForm.openAllToggleBoxes();
        EditUserForm.expectProducts({
            wire: {
                [PRODUCTS.wire.all._id]: false,
                [PRODUCTS.wire.sports._id]: false,
            },
            agenda: {
                [PRODUCTS.agenda.sports._id]: false,
            },
        });
    });
});
