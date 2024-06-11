import React from 'react';
import UserListItem from './UserListItem';
import {gettext} from 'utils';
import {ICompany, IUser} from 'interfaces';

interface IProps {
    users: Array<IUser>;
    onClick: (userId: IUser['_id']) => void;
    activeUserId: string;
    companiesById: Dictionary<ICompany>;
}

function UsersList({users, onClick, activeUserId, companiesById}: IProps) {
    const list = users.map((user: any) =>
        <UserListItem
            key={user._id}
            user={user}
            onClick={onClick}
            isActive={activeUserId === user._id}
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
                            <th>{ gettext('User Id') }</th>
                            <th>{ gettext('Phone') }</th>
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

export default UsersList;
