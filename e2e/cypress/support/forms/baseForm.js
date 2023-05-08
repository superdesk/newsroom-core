import {Input} from '../inputs/input';
import {CheckboxInput} from '../inputs/checkbox';

export class BaseForm {
    constructor(selector) {
        this.selector = selector;
        this.fields = {};
    }

    getFormElement(additionalSelector) {
        return additionalSelector == null ?
            cy.get(this.selector) :
            cy.get(`${this.selector} ${additionalSelector}`);
    }

    getField(name) {
        const field = this.fields[name];

        if (!field) {
            const error = `Error: Field "${name}" not defined for this form`;

            cy.log(error);
            throw error;
        }

        return field;
    }

    type(values) {
        cy.log('Common.Forms.BaseForm.type');
        cy.wrap(Object.keys(values)).each(
            (field) => {
                this.getField(field).type(values[field]);
            }
        );
    }

    expect(values) {
        cy.log('Common.Forms.BaseForm.expect');
        cy.wrap(Object.keys(values)).each(
            (field) => {
                this.getField(field).expect(values[field]);
            }
        );
    }

    getInput(selector) {
        return new Input(this.selector, selector);
    }

    getCheckboxInput(selector) {
        return new CheckboxInput(this.selector, selector);
    }
}
