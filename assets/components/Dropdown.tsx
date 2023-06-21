import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {Dropdown as BootstrapDropdown} from 'bootstrap';

export function Dropdown({children, isActive, icon, label, className, buttonProps}: any) {

    const dropdown: any = React.useRef();
    let dropdownInstance: any = null;

    React.useEffect(() => {
        dropdownInstance = BootstrapDropdown.getOrCreateInstance(dropdown.current, {autoClose: true});

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
        onClick={(event: any) => {
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
                }
            )}
            aria-haspopup="true"
            aria-expanded="false"
            ref={dropdown}
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
    buttonProps: PropTypes.shape({
        textOnly: PropTypes.bool,
    }),
};