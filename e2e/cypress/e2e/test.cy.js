import {setup, addDefaultResources} from '../support/e2e';
import {NewshubLayout} from '../support/pages/layout';
import {NewshubSettingsPage} from '../support/pages/settings_company';

import {NAVIGATIONS} from '../fixtures/navigations';
import {PRODUCTS} from '../fixtures/products';
import {COMPANIES} from '../fixtures/companies';
import {USERS} from '../fixtures/users';


/**
 * Tests:
 *      - public_users:
 *          - Update profile
 *      - company_admins:
 *          - Update user section/product permissions
 *      - site_admins:
 *          - Update company section/product/seat permissions
 */

describe('Newshub e2e tests', () => {
    beforeEach(() => {
        setup();
        addDefaultResources();
    });

    it('Testing Newshub using Cypress', () => {
        NewshubLayout.login('admin@nistrator.org', 'admin');
        NewshubLayout.getSidebarLink('settings').click();
        NewshubSettingsPage.getListItems().should('have.length', 2);
    });
});
