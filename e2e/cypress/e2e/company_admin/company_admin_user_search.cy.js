import {setup, addDefaultResources} from '../../support/e2e';
// Pages & Containers
import {NewshubLayout} from '../../support/pages/layout';
import {CompanyAdminPage} from '../../support/pages/company_admin';

describe('CompanyAdmin', function() {
  beforeEach(() => {
      setup();
      addDefaultResources();
  });

  it('Search behavior in Users tab', function() {
      // Login and navigate to Company admin page
      NewshubLayout.login('foo@bar.com', 'admin');
      NewshubLayout.getSidebarLink('company_admin').click();

      // Switch to Users tab and perform a search
      CompanyAdminPage.clickButton('company-admin--users-btn');

      // Perform a search by typing a query
      CompanyAdminPage.typeInput('top-search-bar', 'foo');

      // Click on the search submit button
      CompanyAdminPage.clickButton('search-submit-button');

      // Verify search results are displayed
      CompanyAdminPage
          .getUserListItems()
          .should('have.length', 1);

      // Switch to Companies tab
      CompanyAdminPage.clickButton('company-admin--companies-btn');

      // Switch back to Users tab
      CompanyAdminPage.clickButton('company-admin--users-btn');

      // Verify the user list is updated after switching back
      CompanyAdminPage
          .getUserListItems()
          .should('have.length', 2);
  });
});
