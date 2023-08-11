import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext} from 'utils';

import {
    newUser,
    fetchUsers,
    setCompany,
    setSort,
    toggleSortDirection,
} from '../actions';
import {setSearchQuery} from 'search/actions';

import Users from './Users';
import ListBar from 'components/ListBar';
import {UserListSortFilter} from './filters/UserListSortFilter';
import {UserListCompanyFilter} from './filters/UserListCompanyFilter';


function UsersApp(props: any): any {
    return ([
        <ListBar
            buttonText={gettext('New User')}
            key="UserBar"
            disabled={props.userToEdit != null}
            onNewItem={props.newUser}
            setQuery={props.setQuery}
            fetch={props.fetchUsers}
        >
            <UserListCompanyFilter
                companies={props.companies}
                company={props.company}
                setCompany={props.setCompany}
                fetchUsers={props.fetchUsers}
            />
            <div className="content-bar-divider" />
            <UserListSortFilter
                sort={props.sort}
                sortDirection={props.sortDirection}
                setSort={props.setSort}
                toggleSortDirection={props.toggleSortDirection}
                fetchUsers={props.fetchUsers}
            />
            <div className="content-bar-divider" />
        </ListBar>,
        <Users key="Users" />
    ]);
}

const mapStateToProps = (state: any) => ({
    companies: state.companies,
    company: state.company,
    sort: state.sort,
    sortDirection: state.sortDirection,
    userToEdit: state.userToEdit,
});

UsersApp.propTypes = {
    users: PropTypes.arrayOf(PropTypes.object),
    userToEdit: PropTypes.object,
    activeUserId: PropTypes.string,
    selectUser: PropTypes.func,
    editUser: PropTypes.func,
    saveUser: PropTypes.func,
    deleteUser: PropTypes.func,
    newUser: PropTypes.func,
    resetPassword: PropTypes.func,
    cancelEdit: PropTypes.func,
    isLoading: PropTypes.bool,
    activeQuery: PropTypes.string,
    totalUsers: PropTypes.number,
    companies: PropTypes.arrayOf(PropTypes.object),
    companiesById: PropTypes.object,
    usersById: PropTypes.object,
    fetchUsers: PropTypes.func,
    setQuery: PropTypes.func,
    errors: PropTypes.object,
    dispatch: PropTypes.func,
    setCompany: PropTypes.func,
    company: PropTypes.string,
    sort: PropTypes.string,
    sortDirection:PropTypes.number,
    setSort: PropTypes.func,
    toggleSortDirection: PropTypes.func,

};

const mapDispatchToProps: any = {
    newUser,
    fetchUsers,
    setQuery: setSearchQuery,
    setCompany,
    setSort,
    toggleSortDirection,
};

export default connect(mapStateToProps, mapDispatchToProps)(UsersApp);
