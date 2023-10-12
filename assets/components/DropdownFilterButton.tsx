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
    hideLabelOnMobile,
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
                <i className={`${icon}`} />
            )}
            {
                noLabelWrap
                    ? label
                    : (
                        <span
                            className={classNames(
                                'nh-dropdown-button__text-label',
                                {
                                    'a11y-only': hideLabel,
                                    'nh-dropdown-button__text-label--hide-on-mobile': hideLabelOnMobile,
                                })
                            }
                        >
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
    hideLabelOnMobile: PropTypes.bool,
};

DropdownFilterButton.defaultProps = {autoToggle: true};

export default DropdownFilterButton;
