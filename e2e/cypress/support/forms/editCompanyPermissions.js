import {BaseForm} from './baseForm';

export class EditCompanyPermissions extends BaseForm {
    constructor() {
        super('');

        this.fields = {
            archive_access: this.getCheckboxInput('[data-test-id="field-archive_access"] input'),
            events_only: this.getCheckboxInput('[data-test-id="field-events_only"] input'),
            restrict_coverage_info: this.getCheckboxInput('[data-test-id="field-restrict_coverage_info"] input'),
            wire: this.getCheckboxInput('[data-test-id="field-wire"] input'),
            agenda: this.getCheckboxInput('[data-test-id="field-agenda"] input'),
        };
    }

    getProductCheckbox(productId) {
        return this.getCheckboxInput(`[data-test-id=field-${productId}] input`);
    }

    getProductSeatInput(productId) {
        return this.getInput(`[data-test-id="field-${productId}_seats"]`, true);
    }

    toggleProducts(products) {
        cy.wrap(Object.keys(products)).each(
            (productId) => {
                this.getProductCheckbox(productId).type(products[productId]);
            }
        );
    }

    expectProducts(products) {
        cy.wrap(Object.keys(products)).each(
            (productId) => {
                this.getProductCheckbox(productId).expect(products[productId]);
            }
        );
    }

    typeProductSeats(products) {
        cy.wrap(Object.keys(products)).each(
            (productId) => {
                this.getProductSeatInput(productId).type(products[productId]);
            }
        );
    }

    expectProductSeats(products) {
        cy.wrap(Object.keys(products)).each(
            (productId) => {
                this.getProductSeatInput(productId).expect(products[productId]);
            }
        )
    }
}
