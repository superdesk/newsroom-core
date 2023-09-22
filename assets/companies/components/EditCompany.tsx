import React from 'react';
import {connect} from 'react-redux';
import classNames from 'classnames';
import {isEmpty} from 'lodash';

import {IAuthProvider, ICompany, ICompanyType, ICountry, IProduct, ISection, IUser} from 'interfaces';
import {ICompanySettingsStore} from '../reducers';
import {gettext, shortDate} from 'utils';
import {
    editCompany,
    toggleCompanySection,
    toggleCompanyProduct,
    updateCompanySeats,
    postCompany,
    setError,
    deleteCompany,
    cancelEdit,
    fetchCompanyUsers,
} from '../actions';
import {getCurrentCompanyForEditor} from '../selectors';

import CompanyPermissions from './CompanyPermissions';
import EditCompanyAPI from './EditCompanyAPI';
import AuditInformation from 'components/AuditInformation';
import {EditCompanyDetails} from './EditCompanyDetails';

interface IStateProps {
    company: ICompany;
    companiesById: {[companyId: string]: ICompany};
    sections: Array<ISection>;
    products: Array<IProduct>;
    errors: {[field: string]: Array<string>} | null;
    users: Array<IUser>;
    companyTypes: Array<ICompanyType>;
    apiEnabled: boolean;
    ssoEnabled: boolean;
    authProviders: Array<IAuthProvider>;
    countries: Array<ICountry>;
}

interface IDispatchProps {
    onChange(event: React.ChangeEvent): void;
    toggleCompanySection(sectionId: ISection['_id']): void;
    toggleCompanyProduct(productId: IProduct['_id'], sectionId: ISection['_id'], enable: boolean): void;
    updateCompanySeats(productId: IProduct['_id'], seats: number): void;
    saveCompany(): void;
    setError(errors: {[field: string]: Array<string>}): void;
    deleteCompany(): void;
    cancelEdit(event?: React.MouseEvent): void;
    fetchCompanyUsers(companyId: ICompany['_id']): void;
}

type IProps = IDispatchProps & IStateProps;

interface IState {
    activeTab: string;
}

class EditCompany extends React.Component<IProps, IState> {
    static propTypes: any;
    tabs: Array<{label: any; name: string}>;

    constructor(props: any) {
        super(props);
        this.handleTabClick = this.handleTabClick.bind(this);
        this.getUsers = this.getUsers.bind(this);
        this.save = this.save.bind(this);
        this.deleteCompany = this.deleteCompany.bind(this);

        this.state = {
            activeTab: 'company-details',
        };
        this.tabs = [
            {label: gettext('Company'), name: 'company-details'},
            {label: gettext('Users'), name: 'users'},
            {label: gettext('Permissions'), name: 'permissions'},
        ];

        if (this.props.apiEnabled) {
            this.tabs.push({label: gettext('API'), name: 'api'});
        }
    }

    handleTabClick(name: string) {
        this.setState({activeTab: name});

        if (name === 'users' && this.props.company._id) {
            this.props.fetchCompanyUsers(this.props.company._id);
        }
    }

    getUsers() {
        if (isEmpty(this.props.users)) {
            return (
                <tr>
                    <td colSpan={2}>{gettext('There are no users in the company.')}</td>
                </tr>
            );
        }

        return this.props.users.map((user: any) => (
            <tr key={user._id}>
                <td>{user.first_name} {user.last_name}</td>
                <td>{shortDate(user._created)}</td>
            </tr>
        ));
    }

    isFormValid() {
        let valid = true;
        const errors: any = {};

        if (!this.props.company.name) {
            errors.name = [gettext('Please provide company name')];
            valid = false;
        }

        this.props.setError(errors);
        return valid;
    }

    save(externalEvent: React.MouseEvent) {
        if (externalEvent) {
            externalEvent.preventDefault();

            if (!this.isFormValid()) {
                this.setState({activeTab: 'company-details'});
                return;
            }
        }

        this.props.saveCompany();
    }

    deleteCompany(event: React.MouseEvent) {
        event.preventDefault();

        if (confirm(gettext('Would you like to delete company: {{name}}', {name: this.props.company.name}))) {
            this.props.deleteCompany();
            this.props.cancelEdit();
        }
    }

    render() {
        const currentAuthProvider =  this.props.authProviders.find(
            (provider) => provider._id === (this.props.company.auth_provider ?? 'newshub')
        );

        return (
            <div
                data-test-id="edit-company-form"
                className={classNames(
                    'list-item__preview',
                    {'list-item__preview--large': this.props.apiEnabled}
                )}
                role={gettext('dialog')}
                aria-label={gettext('Edit Company')}
            >
                <div className='list-item__preview-header'>
                    <h3>{this.props.company.name}</h3>
                    <button
                        id='hide-sidebar'
                        type='button'
                        className='icon-button'
                        aria-label={gettext('Close')}
                        onClick={this.props.cancelEdit}>
                        <i className="icon--close-thin" aria-hidden='true' />
                    </button>
                </div>
                <AuditInformation item={this.props.company} />
                <ul
                    data-test-id="form-tabs"
                    className='nav nav-tabs'
                >
                    {this.tabs.filter((tab: any, index: any) => index === 0 || this.props.company._id).map((tab: any) => (
                        <li key={tab.name} className='nav-item'>
                            <a
                                data-test-id={`tab-${tab.name}`}
                                title={tab.name}
                                className={`nav-link ${this.state.activeTab === tab.name && 'active'}`}
                                href='#'
                                onClick={() => {
                                    this.handleTabClick(tab.name);
                                }}
                            >
                                {tab.label}
                            </a>
                        </li>
                    ))}
                </ul>

                <div className='tab-content'>
                    {this.state.activeTab === 'company-details' &&
                        <div className='tab-pane active' id='company-details'>
                            <EditCompanyDetails
                                company={this.props.company}
                                companyTypes={this.props.companyTypes}
                                users={this.props.users}
                                errors={this.props.errors}
                                onChange={this.props.onChange}
                                save={this.save}
                                deleteCompany={this.deleteCompany}
                                ssoEnabled={this.props.ssoEnabled && currentAuthProvider?.auth_type === 'saml'}
                                authProviders={this.props.authProviders}
                                countries = {this.props.countries}
                            />
                        </div>
                    }
                    {this.state.activeTab === 'users' &&
                        <div className='tab-pane active' id='users'>
                            <table className='table'>
                                <tbody>{this.getUsers()}</tbody>
                            </table>
                        </div>
                    }
                    {this.state.activeTab === 'permissions' && this.props.company._id &&
                        <CompanyPermissions
                            company={this.props.company}
                            sections={this.props.sections}
                            products={this.props.products}
                            save={this.save}
                            onChange={this.props.onChange}
                            toggleCompanySection={this.props.toggleCompanySection}
                            toggleCompanyProduct={this.props.toggleCompanyProduct}
                            updateCompanySeats={this.props.updateCompanySeats}
                        />
                    }
                    {this.props.apiEnabled && this.state.activeTab === 'api' && this.props.company._id && (
                        <EditCompanyAPI
                            company={this.props.company}
                            onEditCompany={this.props.onChange}
                            onSave={this.save}
                            errors={this.props.errors}
                            originalItem={!this.props.company._id ?
                                this.props.company :
                                this.props.companiesById[this.props.company._id]
                            }
                        />
                    )}
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state: ICompanySettingsStore): IStateProps => ({
    company: getCurrentCompanyForEditor(state),
    companiesById: state.companiesById,
    sections: state.sections,
    products: state.products,
    errors: state.errors,
    users: state.companyUsers,
    companyTypes: state.companyTypes,
    apiEnabled: state.apiEnabled,
    ssoEnabled: state.ssoEnabled,
    authProviders: state.authProviders,
    countries: state.countries,
});

const mapDispatchToProps = (dispatch: any): IDispatchProps => ({
    onChange: (event) => dispatch(editCompany(event)),
    toggleCompanySection: (sectionId) => dispatch(toggleCompanySection(sectionId)),
    toggleCompanyProduct: (productId, sectionId, enable) => dispatch(toggleCompanyProduct(productId, sectionId, enable)),
    updateCompanySeats: (productId, seats) => dispatch(updateCompanySeats(productId, seats)),
    saveCompany: () => dispatch(postCompany()),
    setError: (errors) => dispatch(setError(errors)),
    deleteCompany: () => dispatch(deleteCompany()),
    cancelEdit: (event) => dispatch(cancelEdit(event)),
    fetchCompanyUsers: (companyId) => dispatch(fetchCompanyUsers(companyId)),
});

export default connect<
    IStateProps,
    IDispatchProps,
    {},
    ICompanySettingsStore
>(mapStateToProps, mapDispatchToProps)(EditCompany);
