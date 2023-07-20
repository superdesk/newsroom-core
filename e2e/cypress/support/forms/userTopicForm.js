import {BaseForm} from './baseForm';
import {SearchResultsBar} from '../containers/searchResultsBar';

class TopicFormSearchParams extends SearchResultsBar {
    getSearchResultElement(searchType, selector) {
        return cy.get(`[data-test-id="user-topic-editor"] [data-test-id="search-results--${searchType}"] ${selector}`);
    }
}

class UserTopicFormWrapper extends BaseForm {
    constructor() {
        super('[data-test-id="user-topic-editor"]');

        this.fields = {
            name: this.getInput('[data-test-id="field-name"] input'),
            notifications: this.getCheckboxInput('[data-test-id="field-notifications"] input'),
            is_global: this.getCheckboxInput('[data-test-id="field-is_global"] input'),
        };
        this.searchParams = new TopicFormSearchParams();
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

    getFormGroup(name, additionalSelector) {
        let selector = `[data-test-id="topic-form-group--${name}"]`;

        if (additionalSelector != null) {
            selector += ` ${additionalSelector}`;
        }

        return this.getFormElement(selector);
    }

    toggleFormGroup(name) {
        this.getFormGroup(name, '[data-test-id="toggle-btn"]').click();
    }
}

export const UserTopicForm = new UserTopicFormWrapper();
