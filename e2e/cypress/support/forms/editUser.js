import {BaseForm} from './baseForm';

class EditUserFormWrapper extends BaseForm {
    constructor() {
        super('[data-test-id="edit-user-form"]');

        this.fields = {
            first_name: this.getInput('[data-test-id="field-first_name"] input'),
            last_name: this.getInput('[data-test-id="field-last_name"] input'),
            email: this.getInput('[data-test-id="field-email"] input'),
            phone: this.getInput('[data-test-id="field-phone"] input'),
            mobile: this.getInput('[data-test-id="field-mobile"] input'),
            role: this.getInput('[data-test-id="field-role"] input'),
            user_type: this.getInput('[data-test-id="field-user_type"] select'),
            company: this.getSelectInput('[data-test-id="field-company"] select'),
            company_read_only: this.getInput('[data-test-id="field-company"] input'),
            locale: this.getInput('[data-test-id="field-locale"] select'),
            expiry_alert: this.getCheckboxInput('[data-test-id="field-expiry_alert"] input'),
            manage_company_topics: this.getCheckboxInput('[data-test-id="field-manage_company_topics"] input'),
        };
    }

    save(saveId = false) {
        if (saveId) {
            cy.intercept({path: '/users/new', times: 1}).as('newUser');
            this.getFormElement('[data-test-id="save-btn"]').click();
            cy.wait('@newUser').then((interception) => {
                cy.wrap(interception.response.body._id).as('newUserId');
            });
        } else {
            this.getFormElement('[data-test-id="save-btn"]').click();
        }
    }

    getNewlyCreatedUserId(callback) {
        cy.get('@newUserId').then(callback);
    }

    openAllToggleBoxes() {
        this.getFormElement('[data-test-id="toggle--sections"]').click();
        this.getFormElement('[data-test-id="toggle--products"]').click();
        this.getFormElement('[data-test-id="toggle--user-settings"]').click();
    }

    getSectionCheckbox(section) {
        return this.getCheckboxInput(` [data-test-id="field-sections.${section}"] input`);
    }

    getProductCheckbox(section, productId) {
        return this.getCheckboxInput(` [data-test-id="field-products.${section}.${productId}"] input`);
    }

    typeSections(sections) {
        cy.log('EditUserForm.typeSections');
        cy.wrap(Object.keys(sections)).each(
            (section) => {
                this.getSectionCheckbox(section).type(sections[section]);
            }
        );
    }

    expectSections(sections) {
        cy.log('EditUserForm.expectSections');
        cy.wrap(Object.keys(sections)).each(
            (section) => {
                this.getSectionCheckbox(section).expect(sections[section]);
            }
        );
    }

    expectSectionsMissing(sectionIds) {
        cy.log('EditUserForm.expectSectionsMissing');
        cy.wrap(sectionIds).each(
            (section) => {
                this.getSectionCheckbox(section).getElement().should('not.exist');
            }
        );
    }

    typeProducts(products) {
        cy.log('EditUserForm.typeProducts');
        cy.wrap(Object.keys(products)).each(
            (section) => {
                cy.wrap(Object.keys(products[section])).each(
                    (productId) => {
                        this.getProductCheckbox(section, productId).type(products[section][productId]);
                    }
                );
            }
        );
    }
    expectProducts(products) {
        cy.log('EditUserForm.expectProducts');
        cy.wrap(Object.keys(products)).each(
            (section) => {
                cy.wrap(Object.keys(products[section])).each(
                    (productId) => {
                        this.getProductCheckbox(section, productId).expect(products[section][productId]);
                    }
                );
            }
        );
    }

    expectProductsMissing(products) {
        cy.log('EditUserForm.expectProductsMissing');
        cy.wrap(Object.keys(products)).each(
            (section) => {
                cy.wrap(products[section]).each(
                    (productId) => {
                        this.getProductCheckbox(section, productId).getElement().should('not.exist');
                    }
                );
            }
        );
    }
}

export const EditUserForm = new EditUserFormWrapper();
