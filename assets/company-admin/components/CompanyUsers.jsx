import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {selectUser as _selectUser} from 'users/actions';
import {currentCompanySelector, companySectionListSelector} from '../selectors';

import {CompanyUserListItem} from './CompanyUserListItem';

function CompanyUsersComponent({users, usersById, selectUser, activeUserId, currentCompany, companySections}) {
    const sections = companySections[currentCompany._id];

    return (
        <table className="table table-hover table--extended" tabIndex="-1">
            <thead>
                <tr>
                    <th>
                        <div>{gettext('Name')}</div>
                        <div>{gettext('Email')}</div>
                    </th>
                    <th>{gettext('Status')}</th>
                    {sections.map((section) => (
                        <th key={section._id}>
                            {gettext('{{ section }} Products', {section: section.name})}
                        </th>
                    ))}
                    <th>
                        <div>{gettext('Created on')}</div>
                        <div>{gettext('Last active')}</div>
                    </th>
                </tr>
            </thead>
            <tbody>
                {users.map((userId) => (
                    <CompanyUserListItem
                        key={userId}
                        user={usersById[userId]}
                        onClick={() => selectUser(userId)}
                        selected={userId === activeUserId}
                        sections={sections}
                    />
                ))}
            </tbody>
        </table>
    );
}

CompanyUsersComponent.propTypes = {
    users: PropTypes.arrayOf(PropTypes.string),
    usersById: PropTypes.object,
    selectUser: PropTypes.func,
    activeUserId: PropTypes.string,
    currentCompany: PropTypes.object,
    companySections: PropTypes.object,
};

const mapStateToProps = (state) => ({
    users: state.users,
    usersById: state.usersById,
    activeUserId: state.activeUserId,
    currentCompany: currentCompanySelector(state),
    companySections: companySectionListSelector(state),
});

const mapDispatchToProps = (dispatch) => ({
    selectUser: (userId) => dispatch(_selectUser(userId)),
});

export const CompanyUsers = connect(mapStateToProps, mapDispatchToProps)(CompanyUsersComponent);
