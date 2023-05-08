import {Input} from './input';

export class CheckboxInput extends Input {
    type(value) {
        if (value) {
            this.getElement().check();
        } else {
            this.getElement().uncheck();
        }
    }

    expect(value) {
        if (value) {
            this.getElement().should('be.checked')
        } else {
            this.getElement().should('not.be.checked');
        }
    }
}
