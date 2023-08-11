import React from 'react';
import PropTypes from 'prop-types';
import UserListItem from './UserListItem';
import {gettext} from 'utils';


function UsersList({users, onClick, activeUserId, companiesById}: any) {
    const list = users.map((user: any) =>
        <UserListItem
            key={user._id}
            user={user}
            onClick={onClick}
            isActive={activeUserId===user._id}
            companiesById={companiesById} />
    );

    return (
        <section className="content-main">
            <div className="list-items-container">
                <table
                    className="table table-hover"
                    data-test-id="user-list"
                >
                    <thead>
                        <tr>
                            <th>{ gettext('Name') }</th>
                            <th>{ gettext('Email') }</th>
                            <th>{ gettext('Phone') }</th>
                            <th>{ gettext('Mobile') }</th>
                            <th>{ gettext('Role') }</th>
                            <th>{ gettext('User Type') }</th>
                            <th>{ gettext('Company') }</th>
                            <th>{ gettext('Status') }</th>
                            <th>{ gettext('Created On') }</th>
                            <th>{ gettext('Last Active') }</th>
                        </tr>
                    </thead>
                    <tbody>{list}</tbody>
                </table>
            </div>
        </section>
    );
}

UsersList.propTypes = {
    users: PropTypes.array.isRequired,
    onClick: PropTypes.func.isRequired,
    activeUserId: PropTypes.string,
    companiesById: PropTypes.object,
};

export default UsersList;
