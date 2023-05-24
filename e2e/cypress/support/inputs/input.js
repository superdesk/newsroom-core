
export class Input {
    constructor(parentSelector, selector, clearBeforeTyping = true) {
        this.parentSelector = parentSelector;
        this.selector = selector;
        this.clearBeforeTyping = clearBeforeTyping;
    }

    getElement() {
        return cy.get(this.parentSelector + ' ' + this.selector);
    }

    type(value) {
        if (this.clearBeforeTyping) {
            this.getElement().clear().type(value);
        } else {
            this.getElement().type(value);
        }
    }

    expect(value) {
        this.getElement().should('have.value', value);
    }
}

export class SelectInput extends Input {
    type(value) {
        this.getElement().select(value);
    }
}
