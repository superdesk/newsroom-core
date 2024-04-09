class FilterPanelWrapper {
    openPanel() {
        cy.get('[data-test-id="toggle-filter-panel"]').click();
    }

    openFiltersTab() {
        cy.get('[data-test-id="filter-panel-tab--filters"]').click();
    }

    selectFilter(value) {
        cy.get(`[data-test-id="filter"][data-test-value="${value}"] input`).check();
    }

    button(value) {
        cy.get(`[data-test-id="filter-panel--${value}-btn"]`).click();
    }

    selectNowDate() {
        cy.get('[data-test-id="nav-link--today"]').click();
    }
}

export const FilterPanel = new FilterPanelWrapper();
