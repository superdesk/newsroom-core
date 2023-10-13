import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

function DropdownFilterButton({
    id,
    isActive,
    autoToggle,
    onClick,
    icon,
    label,
    hideLabel,
    borderless,
    noLabelWrap,
}: any) {
    return (
        <button
            id={id}
            type="button"
            className={classNames(
                {
                    'nh-dropdown-button--borderless': borderless,
                    'nh-dropdown-button': !borderless,
                    'nh-dropdown-button--active': isActive,
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
            {
                noLabelWrap
                    ? label
                    : (
                        <span style={hideLabel ? {display: 'none'} : {}} className="nh-dropdown-button__text-label">
                            {label}
                        </span>
                    )
            }
            <i className='nh-dropdown-button__caret icon-small--arrow-down' />
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
    hideLabel: PropTypes.bool,
    borderless: PropTypes.bool,
    noLabelWrap: PropTypes.bool,
};

DropdownFilterButton.defaultProps = {autoToggle: true};

export default DropdownFilterButton;
