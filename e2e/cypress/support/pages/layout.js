
class NewshubLayoutWrapper {
    login(email, password) {
        cy.get('#email').type(email);
        cy.get('#password').type(password);
        cy.get('button[type=submit]').click();
    }

    getSidebarLink(name) {
        return cy.get(`[data-test-id="sidenav-link-${name}"]`);
    }

    getAvatar() {
        return cy.get('[data-test-id="header-avatar"]');
    }
}

export const NewshubLayout = new NewshubLayoutWrapper();
