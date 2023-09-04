import * as React from 'react';
import {get, sortBy} from 'lodash';

import {ICompany, IAuthProvider, IUser, ICountry, ICompanyType} from 'interfaces';

import {getDateInputDate, gettext, isInPast} from 'utils';
import TextInput from 'components/TextInput';
import SelectInput from 'components/SelectInput';
import DateInput from 'components/DateInput';
import CheckboxInput from 'components/CheckboxInput';

interface IProps {
    company: ICompany;
    companyTypes: Array<ICompanyType>;
    users: Array<IUser>;
    errors: {[field: string]: Array<string>} | null;
    onChange(event: React.ChangeEvent): void;
    save(event: React.MouseEvent): void;
    deleteCompany(event: React.MouseEvent): void;
    ssoEnabled: boolean;
    authProviders: Array<IAuthProvider>;
    countries: Array<ICountry>;
}

export function EditCompanyDetails({
    company,
    companyTypes,
    users,
    errors,
    onChange,
    save,
    deleteCompany,
    ssoEnabled,
    authProviders,
    countries,
}: IProps) {
    return (
        <form>
            <div className="list-item__preview-form">
                <TextInput
                    name='name'
                    label={gettext('Name')}
                    value={company.name}
                    onChange={onChange}
                    error={errors ? errors.name : null}
                />

                {authProviders.length <= 1 ? null : (
                    <SelectInput
                        name="auth_provider"
                        label={gettext('Authentication Provider')}
                        value={company.auth_provider || 'newshub'}
                        options={authProviders.map((provider) => ({
                            value: provider._id,
                            text: provider.name,
                        }))}
                        onChange={onChange}
                        error={errors?.auth_provider}
                    />
                )}

                {ssoEnabled && (
                    <TextInput
                        name='auth_domain'
                        label={gettext('SSO domain')}
                        value={company.auth_domain || ''}
                        onChange={onChange}
                        error={errors ? errors.auth_domain : null}
                    />
                )}

                <SelectInput
                    name='company_type'
                    label={gettext('Company Type')}
                    value={company.company_type || ''}
                    options={companyTypes.map((ctype) => ({text: gettext(ctype.name), value: ctype.id}))}
                    defaultOption=""
                    onChange={onChange}
                    error={errors ? errors.company_type : undefined}
                />

                <TextInput
                    name='url'
                    label={gettext('Company Url')}
                    value={company.url}
                    onChange={onChange}
                    error={errors ? errors.url : null}
                />

                <TextInput
                    name='sd_subscriber_id'
                    label={gettext('Superdesk Subscriber Id')}
                    value={company.sd_subscriber_id}
                    onChange={onChange}
                    error={errors ? errors.sd_subscriber_id : null}
                />

                <TextInput
                    name='account_manager'
                    label={gettext('Account Manager')}
                    value={company.account_manager}
                    onChange={onChange}
                    error={errors ? errors.account_manager : null}
                />

                <TextInput
                    name='phone'
                    label={gettext('Telephone')}
                    value={company.phone}
                    onChange={onChange}
                    error={errors ? errors.phone : null}
                />

                <TextInput
                    name='contact_name'
                    label={gettext('Contact Name')}
                    value={company.contact_name}
                    onChange={onChange}
                    error={errors ? errors.contact_name : null}
                />

                <TextInput
                    name='contact_email'
                    label={gettext('Contact Email')}
                    value={company.contact_email}
                    onChange={onChange}
                    error={errors ? errors.contact_email : null}
                />

                <SelectInput
                    name='country'
                    label={gettext('Country')}
                    value={company.country}
                    options={countries}
                    onChange={onChange}
                    error={errors ? errors.country : undefined}
                />

                <DateInput
                    name={'expiry_date'}
                    label={gettext('Expiry Date')}
                    value={getDateInputDate(company.expiry_date)}
                    onChange={onChange}
                    error={errors ? errors.expiry_date : null}
                />

                {get(company, 'sections.monitoring') && <SelectInput
                    name='monitoring_administrator'
                    label={gettext('{{monitoring}} Administrator', window.sectionNames)}
                    value={company.monitoring_administrator}
                    options={sortBy(users || [], 'first_name').map((u: any) => ({
                        text: `${u.first_name} ${u.last_name}`,
                        value: u._id}))}
                    defaultOption=""
                    onChange={onChange}
                />}

                <CheckboxInput
                    labelClass={isInPast(company.expiry_date) ? 'text-danger' : ''}
                    name='is_enabled'
                    label={gettext('Enabled')}
                    value={company.is_enabled}
                    onChange={onChange}
                />

            </div>
            <div className='list-item__preview-footer'>
                {company._id && <input
                    type='button'
                    className='nh-button nh-button--secondary'
                    value={gettext('Delete')}
                    onClick={deleteCompany}
                />}
                <input
                    data-test-id="save-btn"
                    type='button'
                    className='nh-button nh-button--primary'
                    value={gettext('Save')}
                    onClick={save}
                />
            </div>
        </form>
    );
}
