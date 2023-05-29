import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {gettext, fullDate} from 'utils';

export function getUserStateLabelDetails(user) {
    if (user.is_approved && user.is_enabled && user.is_validated) {
        return {
            colour: 'green',
            text: gettext('active'),
        };
    } else if (!user.is_approved || !user.is_validated) {
        return {
            colour: 'orange2',
            text: gettext('pending'),
        };
    } else {
        return {
            colour: 'red',
            text: gettext('disabled'),
        };
    }
}

export function CompanyUserListItem({user, onClick, selected, sections}) {
    const stateLabelDetails = getUserStateLabelDetails(user);
    const productNumbers = sections.reduce((sectionProductCount, section) => {
        sectionProductCount[section._id] = (user.products || [])
            .filter((product) => product.section === section._id)
            .length;

        return sectionProductCount;
    }, {});

    return (
        <tr
            onClick={onClick}
            className={!selected ? undefined : 'table--selected'}
            tabIndex="0"
        >
            <td>
                <div className="name">
                    {user.first_name} {user.last_name}
                    {user.user_type === 'company_admin' ?
                        <label className="label label--restricted label--rounded label--fill">
                            {gettext('company admin')}
                        </label>
                        : user.user_type === 'administrator' ?
                            <label className="label label--restricted label--rounded label--fill">
                                {gettext('admin')}
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

            {sections.map((section) => (
                <td key={section._id}>
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
