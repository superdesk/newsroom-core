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
            company: this.getInput('[data-test-id="field-company"] select'),
            company_read_only: this.getInput('[data-test-id="field-company"] input'),

            locale: this.getInput('[data-test-id="field-locale"] select'),

            is_approved: this.getCheckboxInput('[data-test-id="field-is_approved"] input'),
            is_enabled: this.getCheckboxInput('[data-test-id="field-is_enabled"] input'),
            expiry_alert: this.getCheckboxInput('[data-test-id="field-expiry_alert"] input'),
            manage_company_topics: this.getCheckboxInput('[data-test-id="field-manage_company_topics"] input'),
        };
    }

    save() {
        this.getFormElement('[data-test-id="save-btn"]').click();
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
        cy.wrap(Object.keys(sections)).each(
            (section) => {
                this.getSectionCheckbox(section).type(sections[section]);
            }
        )
    }

    expectSections(sections) {
        cy.wrap(Object.keys(sections)).each(
            (section) => {
                this.getSectionCheckbox(section).expect(sections[section]);
            }
        );
    }

    typeProducts(products) {
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
}

export const EditUserForm = new EditUserFormWrapper();
