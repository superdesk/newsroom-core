
export class Input {
    constructor(parentSelector, selector) {
        this.parentSelector = parentSelector;
        this.selector = selector;
    }

    getElement() {
        return cy.get(this.parentSelector + ' ' + this.selector);
    }

    type(value) {
        this.getElement().clear().type(value);
    }

    expect(value) {
        this.getElement().should('have.value', value);
    }
}
