import React from 'react';
import PropTypes from 'prop-types';
import classnames from 'classnames';

import NavLink from './NavLink';
import {gettext} from 'assets/utils';

export default function FilterButton({label, onClick, className, primary}: any) {
    return (
        <div className={classnames('filter-button', className)}>
            <NavLink isActive={primary} onClick={onClick} label={gettext(label)} />
        </div>
    );
}

FilterButton.propTypes = {
    label: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,
    className: PropTypes.string.isRequired,
    primary: PropTypes.bool,
};
