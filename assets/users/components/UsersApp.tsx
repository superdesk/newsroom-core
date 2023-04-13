import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {
    newUser,
    fetchUsers,
    setCompany,
    setSort,
    toggleSortDirection,
} from '../actions';
import Users from './Users';
import {UserListSortFilter} from './filters/UserListSortFilter';
import {UserListCompanyFilter} from './filters/UserListCompanyFilter';
import ListBar from 'assets/components/ListBar';
import {setSearchQuery} from 'assets/search/actions';
import {gettext} from 'assets/utils';


function UsersApp(props: any) {
    return ([
        <ListBar
            key="UserBar"
            onNewItem={props.newUser}
            setQuery={props.setQuery}
            fetch={props.fetchUsers}
            buttonText={gettext('New User')}
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

const mapDispatchToProps = {
    newUser,
    fetchUsers,
    setQuery: setSearchQuery,
    setCompany,
    setSort,
    toggleSortDirection,
};

export default connect(mapStateToProps, mapDispatchToProps)(UsersApp);
