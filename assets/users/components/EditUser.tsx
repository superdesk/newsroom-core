/* eslint-disable react/prop-types */
import React from 'react';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {ICompany, IProduct} from '../../interfaces';

import TextInput from 'components/TextInput';
import SelectInput from 'components/SelectInput';
import CheckboxInput from 'components/CheckboxInput';
import AuditInformation from 'components/AuditInformation';
import {EditUserProductPermission} from './EditUserProductPermission';

import {gettext} from 'utils';
import {
    isUserAdmin,
    getUserTypes,
    getUserLabel,
    userTypeReadOnly,
    getLocaleInputOptions,
    getDefaultLocale,
    isUserCompanyAdmin,
} from '../utils';
import {FormToggle} from 'ui/components/FormToggle';

import {getUserStateLabelDetails} from 'company-admin/components/CompanyUserListItem';

import {companyProductSeatsSelector, companySectionListSelector, sectionListSelector} from 'company-admin/selectors';
import {IUser} from 'interfaces/user';
import {IUserProfileStore} from 'user-profile/reducers';

const getCompanyOptions = (companies: Array<ICompany>) => companies.map((company) => ({value: company._id, text: company.name}));

interface IReduxStoreProps {
    allSections: Array<any>;
    companySections: any;
    seats: any;
}

interface IProps extends IReduxStoreProps {
    original: IUser;
    user: IUser;
    onChange: (event: any) => void;
    errors: any;
    companies: Array<ICompany>;
    onSave: (event: any) => void;
    onResetPassword: () => void;
    onClose: (event: any) => void;
    onDelete: (event: any) => void;
    currentUser: IUser;
    products: Array<IProduct>;
    resendUserInvite: () => void;
    hideFields: Array<string>;
    toolbar?: any;

}

const EditUserComponent: React.ComponentType<IProps> = ({
    original,
    user,
    onChange,
    errors,
    companies,
    onSave,
    onResetPassword,
    onClose,
    onDelete,
    currentUser,
    toolbar,
    products,
    hideFields,
    allSections,
    companySections,
    seats,
    resendUserInvite,
}) => {
    const companyId = user.company;
    const localeOptions = getLocaleInputOptions();
    const stateLabelDetails = getUserStateLabelDetails(user);
    const companyProductIds = companyId != null
        ? Object.keys(seats[companyId] || {})
        : products.map((product: any) => product._id);
    const sections = companyId != null ? companySections[companyId] || [] : allSections;
    const companySectionIds = sections.map((section: any) => section._id);
    const currentUserIsAdmin = isUserAdmin(currentUser);
    const isCompanyAdmin = isUserCompanyAdmin(currentUser);
    const company = companies.find((c) => c._id === user.company);
    const userIsAdmin = isUserAdmin(user);
    const showResendInvite = (user._id == null || user.is_validated === true) && (
        (company?.auth_provider ?? 'newshub') === 'newshub'
    );

    return (
        <div
            data-test-id="edit-user-form"
            className='list-item__preview' role={gettext('dialog')}
            aria-label={gettext('Edit User')}
        >
            <div className='list-item__preview-header'>
                <h3>{ gettext('Add/Edit User') }</h3>
                <button
                    id='hide-sidebar'
                    type='button'
                    className='icon-button'
                    data-bs-dismiss='modal'
                    aria-label={gettext('Close')}
                    onClick={onClose}>
                    <i className="icon--close-thin icon--gray" aria-hidden='true'></i>
                </button>
            </div>
            <AuditInformation item={user} />
            <div className="list-item__preview-content">
                {toolbar ? toolbar : (
                    <div className="list-item__preview-toolbar">
                        <div className="list-item__preview-toolbar-left">
                            <label className={`label label--${stateLabelDetails.colour} label--big label--rounded`}>
                                {stateLabelDetails.text}
                            </label>
                            {user.user_type !== 'administrator' ? null : (
                                <label className="label label--green label--fill label--big label--rounded">
                                    {gettext('admin')}
                                </label>
                            )}
                            {!showResendInvite ? null : (
                                <button
                                    type="button"
                                    className="icon-button icon-button--small icon-button--secondary"
                                    aria-label={gettext('Resend Invite')}
                                    title={gettext('Resend Invite')}
                                    onClick={(event: any) => {
                                        event.preventDefault();

                                        if (confirm(gettext('Would you like to resend the invitation for {{ email }}?', {email: user.email}))) {
                                            resendUserInvite();
                                        }
                                    }}
                                >
                                    <i className="icon--refresh" role="presentation"></i>
                                </button>
                            )}
                        </div>
                        {(currentUserIsAdmin && user._id != null && user._id !== currentUser._id) && (
                            <div className="list-item__preview-toolbar-right">
                                <form method="POST" action={'/auth/impersonate'}>
                                    <input type="hidden" name="user" value={user._id} />
                                    <button
                                        type="submit"
                                        className="nh-button nh-button--tertiary nh-button--small"
                                        aria-label={gettext('Impersonate User')}
                                        data-test-id="impersonate-user-btn"
                                    >
                                        {gettext('Impersonate User')}
                                    </button>
                                </form>
                            </div>
                        )}
                    </div>
                )}
                <form>
                    <div className="list-item__preview-form pt-0">
                        <FormToggle
                            expanded={true}
                            title={gettext('General')}
                            testId="toggle--general"
                        >
                            {hideFields.includes('first_name') ? null : (<TextInput
                                name='first_name'
                                label={gettext('First Name')}
                                value={user.first_name}
                                onChange={onChange}
                                error={errors ? errors.first_name : null} />)}

                            {hideFields.includes('last_name') ? null : (<TextInput
                                name='last_name'
                                label={gettext('Last Name')}
                                value={user.last_name}
                                onChange={onChange}
                                error={errors ? errors.last_name : null} />)}

                            {hideFields.includes('email') ? null : (<TextInput
                                name='email'
                                label={gettext('Email')}
                                value={user.email}
                                onChange={onChange}
                                error={errors ? errors.email : null} />)}

                            {hideFields.includes('phone') ? null : (<TextInput
                                name='phone'
                                label={gettext('Phone')}
                                value={user.phone}
                                onChange={onChange}
                                error={errors ? errors.phone : null} />)}

                            {hideFields.includes('mobile') ? null : (<TextInput
                                name='mobile'
                                label={gettext('Mobile')}
                                value={user.mobile}
                                onChange={onChange}
                                error={errors ? errors.mobile : null} />)}

                            {hideFields.includes('role') ? null : (<TextInput
                                name='role'
                                label={gettext('Role')}
                                value={user.role}
                                onChange={onChange}
                                error={errors ? errors.role : null} />)}
                            {hideFields.includes('user_type') ? null : (<SelectInput
                                name='user_type'
                                label={gettext('User Type')}
                                value={user.user_type}
                                options={userTypeReadOnly(user, currentUser) ? [] : getUserTypes(currentUser) }
                                defaultOption={userTypeReadOnly(user, currentUser) ? getUserLabel(user.user_type) : undefined}
                                readOnly={userTypeReadOnly(user, currentUser) || isUserCompanyAdmin(currentUser)}
                                onChange={onChange}
                                error={errors ? errors.user_type : null}/>)}
                            {hideFields.includes('company') ? (
                                <TextInput
                                    name='company'
                                    label={gettext('Company')}
                                    value={company?.name}
                                    onChange={onChange}
                                    readOnly={isUserCompanyAdmin(currentUser)}
                                    error={errors ? errors.company : null}
                                />
                            ) : (
                                <SelectInput
                                    name='company'
                                    label={gettext('Company')}
                                    value={user.company}
                                    defaultOption={''}
                                    options={getCompanyOptions(companies)}
                                    onChange={onChange}
                                    error={errors ? errors.company : null}
                                />
                            )}

                            {(!localeOptions.length || hideFields.includes('language')) ? null : (
                                <SelectInput
                                    name={'locale'}
                                    label={gettext('Language')}
                                    value={user.locale}
                                    onChange={onChange}
                                    options={localeOptions}
                                    defaultOption={getDefaultLocale()}
                                    error={errors ? errors.locale : null}
                                />
                            )}
                        </FormToggle>

                        {(userIsAdmin || hideFields.includes('sections')) ? null : (
                            <FormToggle
                                title={gettext('Sections')}
                                testId="toggle--sections"
                            >
                                {sections.filter((section: any) => companySectionIds.includes(section._id)).map((section: any) => (
                                    <div className="list-item__preview-row" key={section._id}>
                                        <div className="form-group">
                                            <CheckboxInput
                                                name={`sections.${section._id}`}
                                                label={section.name}
                                                value={get(user, `sections.${section._id}`) === true}
                                                onChange={onChange}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </FormToggle>
                        )}

                        {(userIsAdmin || hideFields.includes('products')) ? null : (
                            <FormToggle
                                title={gettext('Products')}
                                testId="toggle--products"
                            >
                                {isCompanyAdmin ? <div className="products-list__heading d-flex justify-content-between align-items-center">
                                    <button type='button' name='selectAllBtn' className='nh-button nh-button--tertiary nh-button--small' onClick={onChange} >
                                        {gettext('Select All')}
                                    </button>
                                </div> : null}
                                {sections.filter((section: any) => (
                                    companySectionIds.includes(section._id) &&
                                    get(user, `sections.${section._id}`) === true
                                )).map((section: any) => (
                                    <React.Fragment key={section._id}>
                                        <div className="list-item__preview-subheading">
                                            {section.name}
                                        </div>
                                        {products.filter(
                                            (product: any) => product.product_type === section._id &&
                                                companyProductIds.includes(product._id)
                                        ).map((product: any) => (
                                            <EditUserProductPermission
                                                key={product._id}
                                                original={original}
                                                user={user}
                                                section={section}
                                                product={product}
                                                seats={seats}
                                                onChange={onChange}
                                            />
                                        ))}
                                    </React.Fragment>
                                ))}
                            </FormToggle>
                        )}

                        <FormToggle
                            title={gettext('User Settings')}
                            testId="toggle--user-settings"
                        >
                            {hideFields.includes('is_approved') ? null : (<div className="list-item__preview-row">
                                <div className="form-group">
                                    <CheckboxInput
                                        name='is_approved'
                                        label={gettext('Approved')}
                                        value={user.is_approved === true}
                                        onChange={onChange} />
                                </div>
                            </div>)}

                            {hideFields.includes('is_enabled') ? null : (<div className="list-item__preview-row">
                                <div className="form-group">
                                    <CheckboxInput
                                        name='is_enabled'
                                        label={gettext('Enabled')}
                                        value={user.is_enabled === true}
                                        onChange={onChange} />
                                </div>
                            </div>)}

                            {hideFields.includes('expiry_alert') ? null : (<div className="list-item__preview-row">
                                <div className="form-group">
                                    <CheckboxInput
                                        name='expiry_alert'
                                        label={gettext('Company Expiry Alert')}
                                        value={user.expiry_alert === true}
                                        onChange={onChange} />
                                </div>
                            </div>)}

                            {hideFields.includes('manage_company_topics') ? null : (<div className="list-item__preview-row">
                                <div className="form-group">
                                    <CheckboxInput
                                        name='manage_company_topics'
                                        label={gettext('Manage Company Topics')}
                                        value={user.manage_company_topics === true}
                                        onChange={onChange} />
                                </div>
                            </div>)}
                        </FormToggle>

                    </div>

                    <div className='list-item__preview-footer'>
                        {!user.is_validated || isCompanyAdmin ? null : (
                            <input
                                type='button'
                                className='nh-button nh-button--secondary'
                                value={gettext('Reset Password')}
                                id='resetPassword'
                                onClick={onResetPassword} />
                        )}
                        {user._id && (currentUserIsAdmin||isCompanyAdmin) && user._id !== currentUser._id && <input
                            type='button'
                            className='nh-button nh-button--secondary'
                            value={gettext('Delete')}
                            onClick={onDelete} />}
                        <input
                            data-test-id="save-btn"
                            type='button'
                            className='nh-button nh-button--primary'
                            value={gettext('Save')}
                            onClick={onSave} />
                    </div>
                </form>
            </div>
        </div>
    );
};

const mapStateToProps = (state: IUserProfileStore): IReduxStoreProps => ({
    allSections: sectionListSelector(state),
    companySections: companySectionListSelector(state),
    seats: companyProductSeatsSelector(state),
});

const EditUser = connect<IReduxStoreProps>(mapStateToProps)(EditUserComponent);

export default EditUser;
