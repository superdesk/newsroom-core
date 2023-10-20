import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {gettext, fullDate} from 'utils';

export function getUserStateLabelDetails(user: any) {
    if (user.is_approved && user.is_enabled && user.is_validated) {
        return {
            colour: 'green',
            text: gettext('Active'),
        };
    } else if (!user.is_approved || !user.is_validated) {
        return {
            colour: 'orange2',
            text: gettext('Pending'),
        };
    } else {
        return {
            colour: 'red',
            text: gettext('Disabled'),
        };
    }
}

export function CompanyUserListItem({user, onClick, selected, sections}: any) {
    const stateLabelDetails = getUserStateLabelDetails(user);
    const productNumbers = sections.reduce((sectionProductCount: any, section: any) => {
        sectionProductCount[section._id] = (user.products || [])
            .filter((product: any) => product.section === section._id)
            .length;

        return sectionProductCount;
    }, {});

    return (
        <tr
            data-test-id={`user-list-item--${user._id}`}
            onClick={onClick}
            className={!selected ? undefined : 'table--selected'}
            tabIndex={0}
        >
            <td>
                <div className="name">
                    {user.first_name} {user.last_name}
                    {user.user_type === 'company_admin' ?
                        <label className="label label--restricted label--rounded label--fill">
                            {gettext('Company Admin')}
                        </label>
                        : user.user_type === 'administrator' ?
                            <label className="label label--restricted label--rounded label--fill">
                                {gettext('Admin')}
                            </label> : null}
                </div>
                <div className="email">
                    {user.email}
                </div>
            </td>
            <td>
                <label className={`label label--${stateLabelDetails.colour} label--rounded`}>
                    {stateLabelDetails.text}
                </label>
            </td>

            {sections.map((section: any) => (
                <td key={section._id} data-test-id={`user-seats--${section._id}`}>
                    <span className={classNames(
                        'badge rounded-pill bg-secondary text-dark',
                        {'badge--disabled': !productNumbers[section._id]}
                    )}>
                        {productNumbers[section._id]}
                    </span>
                </td>
            ))}
            <td>
                <div className="time">{fullDate(user._created)}</div>
                {!user.last_active ? null : (
                    <div className="time">{fullDate(user.last_active)}</div>
                )}
            </td>
        </tr>
    );
}

CompanyUserListItem.propTypes = {
    user: PropTypes.object,
    onClick: PropTypes.func,
    selected: PropTypes.bool,
    sections: PropTypes.arrayOf(PropTypes.object),
};
