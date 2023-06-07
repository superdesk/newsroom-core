import {BaseForm} from './baseForm';

class UserTopicFormWrapper extends BaseForm {
    constructor() {
        super('[data-test-id="user-topic-editor"]');

        this.fields = {
            name: this.getInput('[data-test-id="field-name"] input'),
            notifications: this.getCheckboxInput('[data-test-id="field-notifications"] input'),
            is_global: this.getCheckboxInput('[data-test-id="field-is_global"] input'),
        };
    }

    saveTopic(saveId = false) {
        if (saveId) {
            cy.intercept({path: '/users/**/topics', times: 1, method: 'POST'}).as('newTopic');
            this.getFormElement('[data-test-id="save-topic-btn"]').click();
            cy.wait('@newTopic').then((interception) => {
                cy.wrap(interception.response.body._id).as('newTopicId');
            })
        } else {
            this.getFormElement('[data-test-id="save-topic-btn"]').click();
        }
    }

    getNewlyCreatedTopicId(callback) {
        cy.get('@newTopicId').then(callback);
    }
}

export const UserTopicForm = new UserTopicFormWrapper();
