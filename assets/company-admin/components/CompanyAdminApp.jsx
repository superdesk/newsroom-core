import * as React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import classNames from 'classnames';

import {gettext} from 'utils';

import {setProductFilter, setSection} from '../actions';
import {postUser, deleteUser, resetPassword, newUser, cancelEdit, editUser, setError, fetchUsers, setSort, toggleSortDirection} from 'users/actions';
import {setSearchQuery} from 'search/actions';
import {productListSelector, companyListSelector, currentUserSelector} from '../selectors';

import {CompanyDetails} from './CompanyDetails';
import {CompanyUsers} from './CompanyUsers';
import {CompanyAdminSideNav} from './CompanyAdminSideNav';

import ListBar from 'components/ListBar';
import {UserListSortFilter} from 'users/components/filters/UserListSortFilter';
import EditUser from 'users/components/EditUser';
import {CompanyDetailsProductFilter} from './CompanyDetailsProductFilter';
import {CompanyAdminProductSeatRequestModal} from './CompanyAdminProductSeatRequestModal';

class CompanyAdminAppComponent extends React.Component {
    constructor(props) {
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
    }

    toggleSideNav() {
        this.setState({sideNavOpen: !this.state.sideNavOpen});
    }

    isFormValid() {
        let valid = true;
        let errors = {};

        if (!this.props.userToEdit.email) {
            errors.email = [gettext('Please provide email')];
            valid = false;
        }

        this.props.setError(errors);
        return valid;
    }

    saveUser(event) {
        event.preventDefault();

        if (!this.isFormValid()) {
            return;
        }

        this.props.saveUser();
    }

    deleteUser(event) {
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

    setProductFilterQuery(query) {
        this.setState({productFilter: query});
    }

    render() {
        return (
            <React.Fragment>
                <div className="settings-inner">
                    {!this.state.sideNavOpen ? null : <CompanyAdminSideNav />}
                    <div className="content">
                        <ListBar
                            onNewItem={this.props.sectionId !== 'users' ? undefined : this.props.newUser}
                            setQuery={this.props.setQuery}
                            fetch={this.props.sectionId === 'users' ?  this.props.fetchUsers : this.setProductFilterQuery }
                            buttonText={gettext('New User')}
                            enableQueryAction={true}
                            noLeftPadding={true}
                        >
                            <button
                                onClick={this.toggleSideNav}
                                className="icon-button icon-button--border-three-sides"
                                aria-label={gettext('Open Side Navigation')}
                            >
                                <i className={classNames(
                                    'icon--gray',
                                    {
                                        'icon--hamburger': !this.state.sideNavOpen,
                                        'icon--arrow-right icon--rotate-180': this.state.sideNavOpen,
                                    }
                                )} />
                            </button>
                            <div className="btn-group btn-group--navbar">
                                <button
                                    onClick={() => this.props.setSection('my_company')}
                                    className={classNames(
                                        'btn btn-outline-primary',
                                        {active: this.props.sectionId === 'my_company'}
                                    )}
                                >
                                    {gettext('My Company')}
                                </button>
                                <button
                                    onClick={() => this.props.setSection('users')}
                                    className={classNames(
                                        'btn btn-outline-primary',
                                        {active: this.props.sectionId === 'users'}
                                    )}
                                >
                                    {gettext('Users')}
                                </button>
                            </div>

                            {this.props.sectionId === 'users' ? <label className='label label--big label--rounded'>USERS : {
                                this.props.totalUsers}</label> : ''}
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
                                    user={this.props.userToEdit}
                                    onChange={this.props.editUser}
                                    errors={this.props.errors}
                                    companies={this.props.companies}
                                    onSave={this.saveUser}
                                    onResetPassword={this.props.resetPassword}
                                    onClose={this.props.closeUserEditor}
                                    onDelete={this.deleteUser}
                                    currentUser={this.props.user}
                                    products={this.props.products}
                                    hideFields={['user_type', 'company']}
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
    closeUserEditor: PropTypes.func,
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

const mapStateToProps = (state) => ({
    sectionId: state.sectionId,
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

const mapDispatchToProps = (dispatch) => ({
    setSection: (sectionId) => dispatch(setSection(sectionId)),
    newUser: () => dispatch(newUser()),
    editUser: (event) => dispatch(editUser(event)),
    setError: (errors) => dispatch(setError(errors)),
    saveUser: () => dispatch(postUser()),
    closeUserEditor: () => dispatch(cancelEdit()),
    deleteUser: () => dispatch(deleteUser()),
    resetPassword: () => dispatch(resetPassword()),

    setQuery: (query) => dispatch(setSearchQuery(query)),
    fetchUsers: () => dispatch(fetchUsers()),
    setSort: (param) => dispatch(setSort(param)),
    toggleSortDirection: () => dispatch(toggleSortDirection()),
    setProductFilter: (productId) => dispatch(setProductFilter(productId)),
});

export const CompanyAdminApp = connect(mapStateToProps, mapDispatchToProps)(CompanyAdminAppComponent);
