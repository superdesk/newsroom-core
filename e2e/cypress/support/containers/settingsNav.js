
class SettingsNavWrapper {
    getNavLink(name) {
        return cy.get(`[data-test-id="settings-nav--${name}"]`);
    }
}

export const SettingsNav = new SettingsNavWrapper();
