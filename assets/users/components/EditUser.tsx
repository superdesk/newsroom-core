/* eslint-disable react/prop-types */
import React from 'react';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {ICompany, IProduct, ISection} from '../../interfaces';

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
    hasSeatsAvailable,
    seatOccupiedByUser,
} from '../utils';
import {FormToggle} from 'ui/components/FormToggle';

import {getUserStateLabelDetails} from 'company-admin/components/CompanyUserListItem';

import {companyProductSeatsSelector, companySectionListSelector, sectionListSelector} from 'company-admin/selectors';
import {IUser} from 'interfaces/user';
import ActionButton from 'components/ActionButton';

const getCompanyOptions = (companies: Array<ICompany>) => companies.map((company) => ({value: company._id, text: company.name}));

interface IReduxStoreProps {
    allSections: Array<any>;
    companySections: any;
    seats: any;
}

interface IUserProfileStore {
    allSections?: Array<any>;
    companySections?: any;
    seats?: any;
}

interface IProps extends IReduxStoreProps {
    original: IUser;
    user: IUser;

    onChange(user: IUser): void;

    /** @deprecated because it doesn't send changes and relies on DOM manipulation */
    onChange_DEPRECATED: (event: any) => void;

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

const EditUserComponent: React.ComponentType<IProps> = (props: IProps) => {
    const {
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
    } = props;

    const companyId = user.company;
    const localeOptions = getLocaleInputOptions();
    const stateLabelDetails = getUserStateLabelDetails(user);
    const companyProductIds = companyId != null
        ? Object.keys(seats[companyId] || {})
        : products.map((product: any) => product._id);
    const sections: Array<ISection> = companyId != null ? companySections[companyId] || [] : allSections;
    const companySectionIds = sections.map((section: any) => section._id);
    const currentUserIsAdmin = isUserAdmin(currentUser);
    const isCompanyAdmin = isUserCompanyAdmin(currentUser);
    const company = companies.find((c) => c._id === user.company);
    const userIsAdmin = isUserAdmin(user);
    const showResendInvite = (user._id == null || user.is_validated !== true) && (
        (company?.auth_provider ?? 'newshub') === 'newshub'
    );

    const resendInviteButton = {
        name: gettext('Resend Invite'),
        icon: 'refresh',
        tooltip: gettext('Resend Invite'),
        multi: false,
        action: () => {
            if (confirm(gettext('Would you like to resend the invitation for {{ email }}?', {email: user.email}))) {
                resendUserInvite();
            }
        },
    };

    return (
        <div
            data-test-id="edit-user-form"
            className='list-item__preview' role={gettext('dialog')}
            aria-label={gettext('Edit User')}
        >
            <div className='list-item__preview-header'>
                <h3>{gettext('Add/Edit User')}</h3>
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
                                    {gettext('Admin')}
                                </label>
                            )}
                            {!showResendInvite ? null : (
                                <ActionButton
                                    key={resendInviteButton.name}
                                    className="icon-button icon-button--small icon-button--secondary"
                                    aria-label={gettext('Resend Invite')}
                                    action={resendInviteButton}
                                />
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
                                onChange={props.onChange_DEPRECATED}
                                error={errors ? errors.first_name : null} />)}

                            {hideFields.includes('last_name') ? null : (<TextInput
                                name='last_name'
                                label={gettext('Last Name')}
                                value={user.last_name}
                                onChange={props.onChange_DEPRECATED}
                                error={errors ? errors.last_name : null} />)}

                            {hideFields.includes('email') ? null : (<TextInput
                                name='email'
                                label={gettext('Email')}
                                value={user.email}
                                onChange={props.onChange_DEPRECATED}
                                error={errors ? errors.email : null} />)}

                            {hideFields.includes('phone') ? null : (<TextInput
                                name='phone'
                                label={gettext('Phone')}
                                value={user.phone}
                                onChange={props.onChange_DEPRECATED}
                                error={errors ? errors.phone : null} />)}

                            {hideFields.includes('mobile') ? null : (<TextInput
                                name='mobile'
                                label={gettext('Mobile')}
                                value={user.mobile}
                                onChange={props.onChange_DEPRECATED}
                                error={errors ? errors.mobile : null} />)}

                            {hideFields.includes('role') ? null : (<TextInput
                                name='role'
                                label={gettext('Role')}
                                value={user.role}
                                onChange={props.onChange_DEPRECATED}
                                error={errors ? errors.role : null} />)}
                            {hideFields.includes('user_type') ? null : (<SelectInput
                                name='user_type'
                                label={gettext('User Type')}
                                value={user.user_type}
                                options={userTypeReadOnly(user, currentUser) ? [] : getUserTypes(currentUser)}
                                defaultOption={userTypeReadOnly(user, currentUser) ? getUserLabel(user.user_type) : undefined}
                                readOnly={userTypeReadOnly(user, currentUser) || isUserCompanyAdmin(currentUser)}
                                onChange={props.onChange_DEPRECATED}
                                error={errors ? errors.user_type : null} />)}
                            {hideFields.includes('company') ? (
                                <TextInput
                                    name='company'
                                    label={gettext('Company')}
                                    value={company?.name}
                                    onChange={props.onChange_DEPRECATED}
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
                                    onChange={(e) => props.onChange_DEPRECATED({
                                        ...e,
                                        changeType: 'company',
                                    })}
                                    error={errors ? errors.company : null}
                                />
                            )}

                            {(!localeOptions.length || hideFields.includes('language')) ? null : (
                                <SelectInput
                                    name={'locale'}
                                    label={gettext('Language')}
                                    value={user.locale}
                                    onChange={props.onChange_DEPRECATED}
                                    options={localeOptions}
                                    defaultOption={getDefaultLocale()}
                                    error={errors ? errors.locale : null}
                                />
                            )}
                        </FormToggle>

                        {(!currentUserIsAdmin || hideFields.includes('sections')) ? null : (
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
                                                onChange={props.onChange_DEPRECATED}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </FormToggle>
                        )}

                        {(userIsAdmin || hideFields.includes('products')) ? null : (() => {
                            const filteredSections = sections.filter((section: any) => (
                                companySectionIds.includes(section._id) && user.sections ?
                                    get(user, `sections.${section._id}`
                                    ) === true : company?.sections
                            ));

                            const filterProductsForSection = (product: IProduct, section: ISection) =>
                                product.product_type === section._id
                                && companyProductIds.includes(product._id);

                            const productsFromSections = filteredSections
                                .flatMap(
                                    (section) => products.filter((product) => filterProductsForSection(product, section)),
                                );

                            return (
                                <FormToggle
                                    title={gettext('Products')}
                                    testId="toggle--products"
                                >
                                    {user.company != null ? (() => {
                                        if (productsFromSections.length < 1) {
                                            return (
                                                <div>{gettext('No products available')}</div>
                                            );
                                        } else {
                                            return (
                                                <>
                                                    {isCompanyAdmin && (
                                                        <div className="products-list__heading d-flex justify-content-between align-items-center">
                                                            <button
                                                                type='button'
                                                                name='selectAllBtn'
                                                                className='nh-button nh-button--tertiary nh-button--small'
                                                                onClick={() => {
                                                                    onChange({
                                                                        ...user,
                                                                        products: productsFromSections
                                                                            .filter((product) =>
                                                                                hasSeatsAvailable(user.company, seats, product)
                                                                                || seatOccupiedByUser(user, product))
                                                                            .map((product) => ({
                                                                                _id: product._id,
                                                                                section: product.product_type,
                                                                            }))
                                                                    });
                                                                }}
                                                            >
                                                                {gettext('Select All')}
                                                            </button>
                                                        </div>
                                                    )}

                                                    {filteredSections.map((section: any) => (
                                                        <React.Fragment key={section._id}>
                                                            <div className="list-item__preview-subheading">
                                                                {section.name}
                                                            </div>
                                                            {
                                                                products
                                                                    .filter((product) => filterProductsForSection(product, section))
                                                                    .map((product) => (
                                                                        <EditUserProductPermission
                                                                            key={product._id}
                                                                            original={original}
                                                                            user={user}
                                                                            section={section}
                                                                            product={product}
                                                                            seats={seats}
                                                                            onChange={props.onChange_DEPRECATED}
                                                                        />
                                                                    ))
                                                            }
                                                        </React.Fragment>
                                                    ))}
                                                </>
                                            );
                                        }
                                    })() : (
                                        <div className='p-1'>
                                            {gettext('If a company hasn\'t been selected, you can\'t select any products.')}
                                        </div>
                                    )}
                                </FormToggle>
                            );
                        })()}

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
                                        onChange={props.onChange_DEPRECATED} />
                                </div>
                            </div>)}

                            {hideFields.includes('is_enabled') ? null : (<div className="list-item__preview-row">
                                <div className="form-group">
                                    <CheckboxInput
                                        name='is_enabled'
                                        label={gettext('Enabled')}
                                        value={user.is_enabled === true}
                                        onChange={props.onChange_DEPRECATED} />
                                </div>
                            </div>)}

                            {hideFields.includes('expiry_alert') ? null : (<div className="list-item__preview-row">
                                <div className="form-group">
                                    <CheckboxInput
                                        name='expiry_alert'
                                        label={gettext('Company Expiry Alert')}
                                        value={user.expiry_alert === true}
                                        onChange={props.onChange_DEPRECATED} />
                                </div>
                            </div>)}

                            {hideFields.includes('manage_company_topics') ? null : (<div className="list-item__preview-row">
                                <div className="form-group">
                                    <CheckboxInput
                                        name='manage_company_topics'
                                        label={gettext('Manage Company Topics')}
                                        value={user.manage_company_topics === true}
                                        onChange={props.onChange_DEPRECATED} />
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
                        {user._id && (currentUserIsAdmin || isCompanyAdmin) && user._id !== currentUser._id && <input
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
