
class ReportsPageWrapper {
    selectReport = (name) => {
        return cy.get('[data-test-id="company-reports-select"]').select(name);
    };

    runSelectedReport = () => {
        return cy.get('[data-test-id="run-report-button"]').click();
    };

    getReportsTable = () => {
        return cy.get('[data-test-id="reports-table"]');
    };
}

export const ReportsPage = new ReportsPageWrapper();
