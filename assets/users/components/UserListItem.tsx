import React from 'react';
import {gettext, shortDate, fullDate} from 'utils';
import {getUserLabel} from '../utils';
import {ICompany, IUser} from 'interfaces';

interface IProps {
    user: IUser;
    isActive: boolean;
    onClick: (userId: IUser['_id']) => void;
    companiesById: Dictionary<ICompany>;
}

function UserListItem({user, isActive, onClick, companiesById}: IProps) {
    const isCompanyUserNotEnabled  = user.company && companiesById[user.company] && !companiesById[user.company]?.is_enabled;
    const isUserNotEnabled = !user.is_enabled;

    return (
        <tr key={user._id}
            className={`
                ${isActive ? 'table--selected' : ''}
                ${isCompanyUserNotEnabled || isUserNotEnabled ? 'table-secondary' : ''}`
            }
            onClick={() => onClick(user._id)}
            tabIndex={0}
            data-test-id={`user-list-item--${user._id}`}
        >
            <td className="name">{user.first_name} {user.last_name}</td>
            <td>{user.email}</td>
            <td>{user._id}</td>
            <td>{user.phone}</td>
            <td>{user.role}</td>
            <td>{getUserLabel(user.user_type)}</td>
            <td>{(user.company && companiesById ? companiesById[user.company]?.name : null)}</td>
            <td>{(user.is_approved ? gettext('Approved') : gettext('Needs Approval'))} -
                {(user.is_enabled ? gettext('Enabled') : gettext('Disabled'))}</td>
            <td>{shortDate(user._created)}</td>
            <td>{user?.last_active ? fullDate(user?.last_active) : ''}</td>
        </tr>
    );
}

export default UserListItem;
