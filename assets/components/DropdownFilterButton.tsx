import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

function DropdownFilterButton({id, isActive, autoToggle, onClick, icon, label, textOnly}: any) {
    return (
        <button
            id={id}
            type="button"
            className={classNames(
                'nh-dropdown-button',
                {
                    'nh-dropdown-button--active': isActive,
                    'nh-dropdown-button--text-only': textOnly,
                }
            )}
            data-bs-toggle={autoToggle ? 'dropdown' : undefined}
            aria-haspopup="true"
            aria-expanded="false"
            onClick={onClick}
        >
            {!icon ? null : (
                <i className={`${icon} d-md-none`} />
            )}
            {textOnly ? label : (
                <span className="d-none d-md-block">
                    {label}
                </span>
            )}
            <i className='icon-small--arrow-down' />
        </button>
    );
}

DropdownFilterButton.propTypes = {
    id: PropTypes.string,
    isActive: PropTypes.bool,
    autoToggle: PropTypes.bool,
    onClick: PropTypes.func,
    icon: PropTypes.string,
    label: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.node),
        PropTypes.node,
        PropTypes.string
    ]),
    textOnly: PropTypes.bool,
};

DropdownFilterButton.defaultProps = {autoToggle: true};

export default DropdownFilterButton;
