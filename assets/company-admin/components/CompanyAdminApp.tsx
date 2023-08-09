import * as React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import classNames from 'classnames';

import {gettext} from 'utils';

import {setProductFilter, setSection} from '../actions';
import {
    postUser,
    deleteUser,
    resetPassword,
    resendUserInvite,
    newUser,
    cancelEdit,
    editUser,
    setError,
    fetchUsers,
    setSort,
    toggleSortDirection,
} from 'users/actions';
import {setSearchQuery} from 'search/actions';
import {productListSelector, companyListSelector, currentUserSelector} from '../selectors';
import {getConfig} from 'utils';

import {CompanyDetails} from './CompanyDetails';
import {CompanyUsers} from './CompanyUsers';
import {CompanyAdminSideNav} from './CompanyAdminSideNav';

import ListBar from 'components/ListBar';
import {UserListSortFilter} from 'users/components/filters/UserListSortFilter';
import EditUser from 'users/components/EditUser';
import {CompanyDetailsProductFilter} from './CompanyDetailsProductFilter';
import {CompanyAdminProductSeatRequestModal} from './CompanyAdminProductSeatRequestModal';

class CompanyAdminAppComponent extends React.Component<any, any> {
    static propTypes: any;
    modals: any;
    constructor(props: any) {
        super(props);

        this.state = {
            sideNavOpen: false,
            productFilter: '',
        };
        this.modals = {
            productSeatRequest: CompanyAdminProductSeatRequestModal,
        };

        this.toggleSideNav = this.toggleSideNav.bind(this);
        this.saveUser = this.saveUser.bind(this);
        this.setProductFilterQuery = this.setProductFilterQuery.bind(this);
        this.deleteUser = this.deleteUser.bind(this);
    }

    toggleSideNav() {
        this.setState({sideNavOpen: !this.state.sideNavOpen});
    }

    isFormValid() {
        let valid = true;
        const errors: any = {};

        if (!this.props.userToEdit.email) {
            errors.email = [gettext('Please provide email')];
            valid = false;
        }

        this.props.setError(errors);
        return valid;
    }

    saveUser(event: any) {
        event.preventDefault();

        if (!this.isFormValid()) {
            return;
        }

        this.props.saveUser();
    }

    deleteUser(event: any) {
        event.preventDefault();

        confirm(gettext('Would you like to delete user: {{ name }}', {name: this.props.userToEdit.first_name})) &&
            this.props.deleteUser();
    }

    renderModal() {
        if (this.props.modal) {
            const Modal = this.modals[this.props.modal.modal];

            return (
                <Modal data={this.props.modal.data} />
            );
        }

        return null;
    }

    setProductFilterQuery(query: any) {
        this.setState({productFilter: query});
    }

    render() {
        return (
            <React.Fragment>
                <div className="settings-inner">
                    {!this.state.sideNavOpen ? null : <CompanyAdminSideNav />}
                    <div className="content">
                        <ListBar
                            testId="company-admin--navbar"
                            onNewItem={this.props.sectionId !== 'users' ? undefined : this.props.newUser}
                            setQuery={this.props.setQuery}
                            fetch={this.props.sectionId === 'users' ?  this.props.fetchUsers : this.setProductFilterQuery }
                            buttonText={gettext('New User')}
                            enableQueryAction={true}
                            noLeftPadding={true}
                        >
                            {/* <button
                                onClick={this.toggleSideNav}
                                className="icon-button icon-button--border-three-sides d-none d-lg-block"
                                aria-label={gettext('Open Side Navigation')}
                            >
                                <i className={classNames(
                                    'icon--gray',
                                    {
                                        'icon--hamburger': !this.state.sideNavOpen,
                                        'icon--arrow-right icon--rotate-180': this.state.sideNavOpen,
                                    }
                                )} />
                            </button> */}
                            <div className="toggle-button__group toggle-button__group--navbar">
                                <button
                                    onClick={() => this.props.setSection('my_company')}
                                    className={classNames(
                                        'toggle-button',
                                        {'toggle-button--active': this.props.sectionId === 'my_company'}
                                    )}
                                    data-test-id="company-admin--companies-btn"
                                >
                                    {gettext('My Company')}
                                </button>
                                <button
                                    onClick={() => this.props.setSection('users')}
                                    className={classNames(
                                        'toggle-button',
                                        {'toggle-button--active': this.props.sectionId === 'users'}
                                    )}
                                    data-test-id="company-admin--users-btn"
                                >
                                    {gettext('Users')}
                                </button>
                            </div>

                            {this.props.sectionId === 'users' ? <label className='label label--big label--rounded me-2'>{
                                gettext('Users : {{total}}', {total : this.props.totalUsers})}</label> : ''}
                            <div className="content-bar-divider" />
                            {this.props.sectionId !== 'users' ? null : (
                                <React.Fragment>
                                    <CompanyDetailsProductFilter
                                        products={this.props.products}
                                        product={this.props.productId}
                                        setProductFilter={this.props.setProductFilter}
                                    />
                                    <UserListSortFilter
                                        sort={this.props.sort}
                                        sortDirection={this.props.sortDirection}
                                        setSort={this.props.setSort}
                                        toggleSortDirection={this.props.toggleSortDirection}
                                        fetchUsers={this.props.fetchUsers}
                                    />
                                    <div className="content-bar-divider" />
                                </React.Fragment>
                            )}
                        </ListBar>
                        <div className="flex-row">
                            <div className="flex-col flex-column">
                                <section className="content-main">
                                    <div className="list-items-container">
                                        {this.props.sectionId !== 'my_company' ? null : <CompanyDetails productFilter={this.state.productFilter} />}
                                        {this.props.sectionId !== 'users' ? null : <CompanyUsers />}
                                    </div>
                                </section>
                            </div>
                            {this.props.userToEdit == null ? null : (
                                <EditUser
                                    original={this.props.usersById[this.props.userToEdit._id] || {}}
                                    user={this.props.userToEdit}
                                    onChange={this.props.editUser}
                                    errors={this.props.errors}
                                    companies={this.props.companies}
                                    onSave={this.saveUser}
                                    onResetPassword={this.props.resetPassword}
                                    onClose={this.props.closeUserEditor}
                                    onDelete={this.deleteUser}
                                    resendUserInvite={this.props.resendUserInvite}
                                    currentUser={this.props.user}
                                    products={this.props.products}
                                    hideFields={getConfig('allow_companies_to_manage_products') ?
                                        ['company'] :
                                        ['company', 'sections', 'products']
                                    }
                                />
                            )}
                        </div>
                    </div>
                </div>
                {this.renderModal()}
            </React.Fragment>
        );
    }
}

CompanyAdminAppComponent.propTypes = {
    sectionId: PropTypes.string,
    setSection: PropTypes.func,
    editUser: PropTypes.func,
    newUser: PropTypes.func,
    setError: PropTypes.func,
    saveUser: PropTypes.func,
    deleteUser: PropTypes.func,
    resetPassword: PropTypes.func,
    resendUserInvite: PropTypes.func,
    closeUserEditor: PropTypes.func,
    usersById: PropTypes.object,
    user: PropTypes.object,
    userToEdit: PropTypes.object,
    errors: PropTypes.object,
    products: PropTypes.arrayOf(PropTypes.object),
    modal: PropTypes.shape({
        modal: PropTypes.string,
        data: PropTypes.object,
    }),
    setQuery: PropTypes.func,
    fetchUsers: PropTypes.func,
    sort: PropTypes.string,
    sortDirection:PropTypes.number,
    setSort: PropTypes.func,
    toggleSortDirection: PropTypes.func,
    productId: PropTypes.string,
    setProductFilter: PropTypes.func,
    companies: PropTypes.arrayOf(PropTypes.object),
    totalUsers:PropTypes.number
};

const mapStateToProps = (state: any) => ({
    sectionId: state.sectionId,
    usersById: state.usersById,
    user: currentUserSelector(state),
    userToEdit: state.userToEdit,
    errors: state.errors,
    products: productListSelector(state),
    modal: state.modal,
    sort: state.sort,
    sortDirection: state.sortDirection,
    productId: state.productId,
    companies: companyListSelector(state),
    totalUsers:state.totalUsers
});

const mapDispatchToProps = (dispatch: any) => ({
    setSection: (sectionId: any) => dispatch(setSection(sectionId)),
    newUser: () => dispatch(newUser()),
    editUser: (event: any) => dispatch(editUser(event)),
    setError: (errors: any) => dispatch(setError(errors)),
    saveUser: () => dispatch(postUser()),
    closeUserEditor: () => dispatch(cancelEdit()),
    deleteUser: () => dispatch(deleteUser()),
    resetPassword: () => dispatch(resetPassword()),
    resendUserInvite: () => dispatch(resendUserInvite()),

    setQuery: (query: any) => dispatch(setSearchQuery(query)),
    fetchUsers: () => dispatch(fetchUsers()),
    setSort: (param: any) => dispatch(setSort(param)),
    toggleSortDirection: () => dispatch(toggleSortDirection()),
    setProductFilter: (productId: any) => dispatch(setProductFilter(productId)),
});

export const CompanyAdminApp: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(CompanyAdminAppComponent);
