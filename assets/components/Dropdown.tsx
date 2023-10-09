import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {Dropdown as BootstrapDropdown} from 'bootstrap';

export function Dropdown({
    children,
    isActive,
    icon,
    optionLabel,
    label,
    value,
    className,
    small,
    stretch,
    borderless,
    hideLabel,
}: any) {
    const dropdown: any = React.useRef();
    let dropdownInstance: any = null;

    React.useEffect(() => {
        dropdownInstance = BootstrapDropdown.getOrCreateInstance(dropdown.current, {boundary: 'window'} as any);

        function clickOutside() {
            dropdownInstance.hide();
        }

        document.addEventListener('click', clickOutside);

        return () => {
            document.removeEventListener('click', clickOutside);
        };
    });

    return (
        <div
            className={classNames(
                'dropdown',
                className ? className : '',
                icon != null ? 'nh-dropdown-button--with-icon' : ''
            )}
            onClick={(event: any) => {
                event.stopPropagation();
                dropdownInstance.toggle();
            }}
            data-test-id="dropdown-btn"
        >
            <button
                type="button"
                className={classNames(
                    'nh-dropdown-button',
                    {
                        'nh-dropdown-button--borderless': borderless,
                        'nh-dropdown-button--active': isActive,
                        'nh-dropdown-button--small': small,
                        'nh-dropdown-button--stretch': stretch,
                    })
                }
                aria-haspopup="true"
                aria-expanded="false"
                ref={dropdown}
            >
                {!icon ? null : (
                    <i className={icon} />
                )}
                {(isActive && optionLabel) ? (
                    <>
                        <span
                            style={hideLabel ? {display: 'none'} : {}}
                            className='nh-dropdown-button__text-label'
                        >
                            {optionLabel}:
                        </span>
                        <span className='nh-dropdown-button__text-value'>{label}</span>
                    </>
                ) : (
                    <span
                        style={hideLabel ? {display: 'none'} : {}}
                        className='nh-dropdown-button__text-label'
                    >
                        {label}
                    </span>
                )}
                {!value ? null : (
                    <span className="nh-dropdown-button__text-value">
                        {value}
                    </span>
                )}
                <i className='nh-dropdown-button__caret icon-small--arrow-down' />
            </button>
            <div className='dropdown-menu'>
                {children}
            </div>
        </div>
    );
}

Dropdown.propTypes = {
    children: PropTypes.node,
    icon: PropTypes.string,
    label: PropTypes.node,
    value: PropTypes.node,
    isActive: PropTypes.bool,
    className: PropTypes.string,
    autoToggle: PropTypes.bool,
    reset: PropTypes.func,
    small: PropTypes.bool,
    stretch: PropTypes.bool,
    optionLabel: PropTypes.string,
    borderless: PropTypes.bool,
    hideLabel: PropTypes.bool,
    hideLabelMobile: PropTypes.bool,
};
