import * as React from 'react';
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
    editUser_DEPRECATED,
    setError,
    fetchUsers,
    setSort,
    toggleSortDirection,
    editUser,
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
import {IUser} from 'interfaces/user';
import {ICompanyAdminStore} from 'company-admin/reducers';

interface IStateProps {
    sectionId: string;
    usersById: any;
    user: IUser;
    userToEdit: IUser;
    errors: any;
    products: Array<any>;
    modal: {
        modal: string;
        data: any;
    };
    sort: string;
    sortDirection: number;
    productId: string;
    companies: Array<any>;
    totalUsers: number;
}

interface IDispatchProps {
    setSection: (sectionId: string) => any;
    newUser: () => IUser;
    editUser: (nextUser: IUser) => void;
    editUser_DEPRECATED: (event: any) => any;
    setError: (errors: any) => any;
    saveUser: () => any;
    closeUserEditor: () => any;
    deleteUser: () => any;
    resetPassword: () => any;
    resendUserInvite: () => any;
    setQuery: (query: any) => any;
    fetchUsers: () => any;
    setSort: (param: any) => any;
    toggleSortDirection: () => any;
    setProductFilter: (productId: any) => any;
}

type IOwnProps = {
    // empty
}

type IProps = IDispatchProps & IStateProps & IOwnProps;

interface IState {
    sideNavOpen: boolean;
    productFilter: string;
}

class CompanyAdminAppComponent extends React.Component<IProps, IState> {
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
        const coreHiddenFields = this.props.user.user_type === 'company_admin'
            ? ['is_approved', 'is_enabled']
            : [];

        const {userToEdit} = this.props;

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
                                    onClick={() => {
                                        this.props.setSection('my_company');
                                        this.props.setQuery('');
                                    }}
                                    className={classNames(
                                        'toggle-button',
                                        {'toggle-button--active': this.props.sectionId === 'my_company'}
                                    )}
                                    data-test-id="company-admin--companies-btn"
                                >
                                    {gettext('My Company')}
                                </button>
                                <button
                                    onClick={() => {
                                        this.props.setSection('users');
                                        this.props.setQuery('');
                                        this.props.fetchUsers();
                                    }}
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
                            {
                                userToEdit !== null && (
                                    <EditUser
                                        original={userToEdit._id != null ? this.props.usersById[userToEdit._id] : {}}
                                        user={userToEdit}
                                        onChange={this.props.editUser}
                                        onChange_DEPRECATED={this.props.editUser_DEPRECATED}
                                        errors={this.props.errors}
                                        companies={this.props.companies}
                                        onSave={this.saveUser}
                                        onResetPassword={this.props.resetPassword}
                                        onClose={this.props.closeUserEditor}
                                        onDelete={this.deleteUser}
                                        resendUserInvite={this.props.resendUserInvite}
                                        currentUser={this.props.user}
                                        products={this.props.products}
                                        hideFields={[
                                            ...coreHiddenFields,
                                            ...(
                                                getConfig('allow_companies_to_manage_products')
                                                    ? ['company']
                                                    : ['company', 'sections', 'products']
                                            )
                                        ]}
                                    />
                                )
                            }
                        </div>
                    </div>
                </div>
                {this.renderModal()}
            </React.Fragment>
        );
    }
}

const mapStateToProps = (state: ICompanyAdminStore): IStateProps => ({
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

const mapDispatchToProps = (dispatch: any): IDispatchProps => ({
    setSection: (sectionId: any) => dispatch(setSection(sectionId)),
    newUser: () => dispatch(newUser()),
    editUser: (nextUser: IUser) => dispatch(editUser(nextUser)),
    editUser_DEPRECATED: (event: any) => dispatch(editUser_DEPRECATED(event)),
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

export const CompanyAdminApp = connect<
    IStateProps,
    IDispatchProps,
    IOwnProps,
    ICompanyAdminStore
>(mapStateToProps, mapDispatchToProps)(CompanyAdminAppComponent);
