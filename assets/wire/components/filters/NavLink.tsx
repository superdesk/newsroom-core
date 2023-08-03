import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

function NavLink({isActive, onClick, label}: any) {
    return (
        <a
            href=''
            className={classNames('nh-button nh-button--tertiary w-100', {
                'nh-button--active': isActive,
                '': !isActive,
            })}
            onClick={onClick}
            data-test-id={`nav-link--${label.toLowerCase()}`}
        >{label}</a>
    );
}

NavLink.propTypes = {
    label: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,
    isActive: PropTypes.bool.isRequired,
};

export default NavLink;
