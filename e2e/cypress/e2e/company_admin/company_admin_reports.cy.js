import {setup, addDefaultResources} from '../../support/e2e';
import {NewshubLayout} from '../../support/pages/layout';
import {ReportsPage} from '../../support/pages/reports_page';


describe('CompanyAdmin - Reports', function () {
    beforeEach(() => {
        setup();
        addDefaultResources();
    });

    it('CompanyAdmin can see and navigate to reports section', () => {
        // Login and navigate to reports
        NewshubLayout.login('foo@bar.com', 'admin');
        NewshubLayout
            .getSidebarLink('reports')
            .should('have.length', 1);

        NewshubLayout
            .getSidebarLink('reports')
            .click();
    });

    it('CompanyAdmin can run report "Saved My Topics and Company Topics"', () => {
        // Login and navigate to reports
        NewshubLayout.login('foo@bar.com', 'admin');
        NewshubLayout
            .getSidebarLink('reports')
            .click();

        ReportsPage.selectReport('company-and-user-saved-searches');
        ReportsPage.runSelectedReport();

        ReportsPage
            .getReportsTable()
            .should('be.visible');

        // now let's check the content of the report quickly
        ReportsPage
            .getReportsTable()
            .contains('td', 'Foo Bar');

        // only one personal saved topic
        ReportsPage
            .getReportsTable()
            .contains('td[data-test-id="my-topics"]', 1);

        // two company shared topics
        ReportsPage
            .getReportsTable()
            .contains('td[data-test-id="company-topics"]', 2);
    });
});
