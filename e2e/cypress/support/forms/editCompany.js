import {BaseForm} from './baseForm';
import {EditCompanyPermissions} from './editCompanyPermissions';

class EditCompanyFormWrapper extends BaseForm {
    constructor() {
        super('[data-test-id="edit-company-form"]');

        this.fields = {
            name: this.getInput('[data-test-id="field-name"] input'),
            url: this.getInput('[data-test-id="field-url"] input'),
            sd_subscriber_id: this.getInput('[data-test-id="field-sd_subscriber_id"] input'),
            account_manager: this.getInput('[data-test-id="field-account_manager"] input'),
            phone: this.getInput('[data-test-id="field-phone"] input'),
            contact_name: this.getInput('[data-test-id="field-contact_name"] input'),
            contact_email: this.getInput('[data-test-id="field-contact_email"] input'),
            country: this.getSelectInput('[data-test-id="field-country"] select'),
            expiry_date: this.getInput('[data-test-id="field-expiry_date"] input'),
            is_enabled: this.getCheckboxInput('[data-test-id="field-is_enabled"] input'),
        };

        this.permissions = new EditCompanyPermissions();
    }

    save(saveId = false) {
        if (saveId) {
            cy.intercept({path: '/companies/new', times: 1}).as('newCompany');
            this.getFormElement('[data-test-id="save-btn"]').click();
            cy.wait('@newCompany').then((interception) => {
                cy.wrap(interception.response.body._id).as('newCompanyId');
            });
        } else {
            this.getFormElement('[data-test-id="save-btn"]').click();
        }
    }

    getNewlyCreatedCompanyId(callback) {
        cy.get('@newCompanyId').then(callback);
    }

    changeTab(name) {
        this.getFormElement(`[data-test-id="form-tabs"] [data-test-id="tab-${name}"]`).click();
    }
}

export const EditCompanyForm = new EditCompanyFormWrapper();
