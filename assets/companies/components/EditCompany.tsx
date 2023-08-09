import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import classNames from 'classnames';
import {isEmpty} from 'lodash';

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

import CompanyPermissions from './CompanyPermissions';
import EditCompanyAPI from './EditCompanyAPI';
import AuditInformation from 'components/AuditInformation';
import {EditCompanyDetails} from './EditCompanyDetails';

class EditCompany extends React.Component<any, any> {
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

    save(externalEvent: any) {
        if (externalEvent) {
            externalEvent.preventDefault();

            if (!this.isFormValid()) {
                this.setState({activeTab: 'company-details'});
                return;
            }
        }

        this.props.saveCompany();
    }

    deleteCompany(event: any) {
        event.preventDefault();

        if (confirm(gettext('Would you like to delete company: {{name}}', {name: this.props.company.name}))) {
            this.props.deleteCompany('companies');
            this.props.cancelEdit();
        }
    }

    render() {
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
                        <i className="icon--close-thin icon--gray-dark" aria-hidden='true' />
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
                                ssoEnabled={this.props.ssoEnabled}
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
                                this.props.company[this.props.company._id]
                            }
                        />
                    )}
                </div>
            </div>
        );
    }
}

EditCompany.propTypes = {
    company: PropTypes.object.isRequired,
    onChange: PropTypes.func,
    toggleCompanySection: PropTypes.func,
    toggleCompanyProduct: PropTypes.func,
    updateCompanySeats: PropTypes.func,
    errors: PropTypes.object,
    users: PropTypes.arrayOf(PropTypes.object),
    saveCompany: PropTypes.func.isRequired,
    setError: PropTypes.func.isRequired,
    deleteCompany: PropTypes.func.isRequired,
    cancelEdit: PropTypes.func.isRequired,
    fetchCompanyUsers: PropTypes.func.isRequired,
    companyTypes: PropTypes.array,
    apiEnabled: PropTypes.bool,
    ssoEnabled: PropTypes.bool,
    companiesById: PropTypes.object,

    sections: PropTypes.arrayOf(PropTypes.shape({
        _id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
    })),
    products: PropTypes.arrayOf(PropTypes.shape({
        _id: PropTypes.string,
        name: PropTypes.string,
        product_type: PropTypes.string,
    })).isRequired,
    countries : PropTypes.array
};

const mapStateToProps = (state: any) => ({
    company: state.companyToEdit,
    companiesById: state.companiesById,
    sections: state.sections,
    products: state.products,
    errors: state.errors,
    users: state.companyUsers,
    companyTypes: state.companyTypes,
    apiEnabled: state.apiEnabled,
    ssoEnabled: state.ssoEnabled,
    countries: state.countries,
});

const mapDispatchToProps = (dispatch: any) => ({
    onChange: (event: any) => dispatch(editCompany(event)),
    toggleCompanySection: (sectionId: any) => dispatch(toggleCompanySection(sectionId)),
    toggleCompanyProduct: (productId: any, sectionId: any, enable: any) => dispatch(toggleCompanyProduct(productId, sectionId, enable)),
    updateCompanySeats: (productId: any, seats: any) => dispatch(updateCompanySeats(productId, seats)),
    saveCompany: () => dispatch(postCompany()),
    setError: (errors: any) => dispatch(setError(errors)),
    deleteCompany: () => dispatch(deleteCompany()),
    cancelEdit: (event: any) => dispatch(cancelEdit(event)),
    fetchCompanyUsers: (companyId: any) => dispatch(fetchCompanyUsers(companyId)),
});

export default connect(mapStateToProps, mapDispatchToProps)(EditCompany);
