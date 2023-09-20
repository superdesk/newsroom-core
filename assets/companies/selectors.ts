import {ICompany} from 'interfaces';
import {ICompanySettingsStore} from './reducers';
import {assertNever} from 'utils';

export function getCurrentCompanyForEditor(state: ICompanySettingsStore): ICompany {
    // This selector is used in `EditCompany` which should not be rendered when
    // `state.companyToEdit` is not defined. So we `assertNever` here
    if (state.companyToEdit == null) {
        assertNever(state.companyToEdit);
    }

    return state.companyToEdit;
}
