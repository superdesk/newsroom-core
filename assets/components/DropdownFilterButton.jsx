import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

function DropdownFilterButton({id, isActive, autoToggle, onClick, icon, label, textOnly, iconColour}) {
    return (
        <button
            id={id}
            type="button"
            className={classNames(
                'btn btn-sm d-flex align-items-center px-2 ms-2',
                {
                    active: isActive,
                    'btn-text-only': textOnly,
                    'btn-outline-primary': !textOnly,
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
            <i className={classNames(
                'icon-small--arrow-down ms-1',
                {
                    'icon--white': isActive && !iconColour,
                    [`icon--${iconColour}`]: iconColour
                }
            )} />
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
    iconColour: PropTypes.string,
};

DropdownFilterButton.defaultProps = {autoToggle: true};

export default DropdownFilterButton;
