
export class FilterPanelContainer {
    toggleFilterPanel() {
        cy.get('[data-test-id="toggle-filter-panel"]').click();
    }

    selectTab(name) {
        cy.get(`[data-test-id="filter-panel-tab--${name}"] a`).click();
    }

    getCurrentPanel(additionalSelector) {
        let selector = '[data-test-id="tab-panel-content--active"]';

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return cy.get(selector);
    }

    getNavGroup(name, additionalSelector) {
        let selector = `[data-test-id="nav-group--${name}"]`;

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return this.getCurrentPanel(selector);
    }

    getNavGroupInput(group, id) {
        return this.getNavGroup(group, `input[id="${id}"]`);
    }
    // nav-group--category

    type(filterParams) {
        Object.keys(filterParams).forEach((filterName) => {
            filterParams[filterName].forEach((filterValue) => {
                this.getNavGroupInput(filterName, filterValue).check();
            });
        });
    }

    // NavLink
    getTopicButton(name) {
        return this.getCurrentPanel(`[data-test-id="nav-link--${name}"]`);
    }

    runSearch() {
        cy.get('[data-test-id="filter-panel--search-btn"]').click();
    }
}
