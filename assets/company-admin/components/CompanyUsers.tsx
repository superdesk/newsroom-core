import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext, getConfig} from 'utils';
import {selectUser as _selectUser} from 'users/actions';
import {currentCompanySelector, companySectionListSelector, userIdSelector, userIdMapSelector} from '../selectors';

import {CompanyUserListItem} from './CompanyUserListItem';

function CompanyUsersComponent({users, usersById, selectUser, activeUserId, currentCompany, companySections}: any) {
    const allowCompaniesToManageProducts = getConfig('allow_companies_to_manage_products');
    const sections = allowCompaniesToManageProducts ? companySections[currentCompany._id] : [];

    return (
        <table
            className="table table-hover table--extended"
            tabIndex={-1}
            data-test-id="company-admin--users-list"
        >
            <thead>
                <tr>
                    <th>
                        <div>{gettext('Name')}</div>
                        <div>{gettext('Email')}</div>
                    </th>
                    <th>{gettext('Status')}</th>
                    {allowCompaniesToManageProducts && sections.map((section: any) => (
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
                {users.map((userId: any) => (
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

const mapStateToProps = (state: any) => ({
    users: userIdSelector(state),
    usersById: userIdMapSelector(state),
    activeUserId: state.activeUserId,
    currentCompany: currentCompanySelector(state),
    companySections: companySectionListSelector(state),
});

const mapDispatchToProps = (dispatch: any) => ({
    selectUser: (userId: any) => dispatch(_selectUser(userId)),
});

export const CompanyUsers: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(CompanyUsersComponent);
