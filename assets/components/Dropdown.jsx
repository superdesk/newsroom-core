import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {Dropdown as BootstrapDropdown} from 'bootstrap';

export function Dropdown({children, isActive, icon, label, className, buttonProps, small, stretch}) {

    const dropdown = React.useRef();
    let dropdownInstance = null;

    React.useEffect(() => {
        dropdownInstance = BootstrapDropdown.getOrCreateInstance(dropdown.current, {boundary: 'window'});

        function clickOutside() {
            dropdownInstance.hide();
        }

        document.addEventListener('click', clickOutside);

        return () => {
            document.removeEventListener('click', clickOutside);
        };
    });

    const textOnly = (buttonProps || {}).textOnly;

    return (<div
        className={classNames(
            'dropdown',
            className ? className : ''
        )}
        onClick={(event) => {
            event.stopPropagation();
            dropdownInstance.toggle();
        }}
    >
        <button
            type="button"
            className={classNames(
                'nh-dropdown-button',
                {
                    active: isActive,
                    'nh-dropdown-button--text-only': textOnly,
                    'nh-dropdown-button--small': small,
                    'nh-dropdown-button--stretch': stretch,
                }
            )}
            aria-haspopup="true"
            aria-expanded="false"
            ref={dropdown}
        >
            {!icon ? null : (
                <i className={icon} />
            )}
            {textOnly ? label : (
                <span className="nh-dropdown-button__text-label">
                    {label}
                </span>
            )}
            <i className='nh-dropdown-button__caret icon-small--arrow-down' />
        </button>
        <div className='dropdown-menu'>
            {children}
        </div>
    </div>);
}

Dropdown.propTypes = {
    children: PropTypes.node,
    icon: PropTypes.string,
    label: PropTypes.node,
    isActive: PropTypes.bool,
    className: PropTypes.string,
    autoToggle: PropTypes.bool,
    reset: PropTypes.func,
    small: PropTypes.bool,
    stretch: PropTypes.bool,
    buttonProps: PropTypes.shape({
        textOnly: PropTypes.bool,
    }),
};