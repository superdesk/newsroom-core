import {BaseForm} from './baseForm';

class AdvancedSearchFormWrapper extends BaseForm {
    constructor() {
        super('[data-test-id="advanced-search-panel"]');

        this.fields = {
            all: this.getInput('[data-test-id="field-all"] textarea'),
            any: this.getInput('[data-test-id="field-any"] textarea'),
            exclude: this.getInput('[data-test-id="field-none"] textarea'),
            'fields.headline': this.getCheckboxInput('[data-test-id="field-headline"] input'),
            'fields.slugline': this.getCheckboxInput('[data-test-id="field-slugline"] input'),
            'fields.body_html': this.getCheckboxInput('[data-test-id="field-body_html"] input'),
        }
    }

    runSearch() {
        this.getFormElement('[data-test-id="run-advanced-search-btn"]').click();
    }
}

export const AdvancedSearchForm = new AdvancedSearchFormWrapper();
