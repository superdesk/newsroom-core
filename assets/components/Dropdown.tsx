import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {Dropdown as BootstrapDropdown} from 'bootstrap';

export function Dropdown({children, isActive, icon, label, className, buttonProps}) {

    const dropdown = React.useRef();
    let dropdownInstance = null;

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
    const iconColour= (buttonProps || {}).iconColour;

    return (<div
        className={classNames(
            'dropdown',
            'btn-group',
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
                'btn btn-sm d-flex align-items-center px-2 ms-1',
                {
                    active: isActive,
                    'btn-text-only': textOnly,
                    'btn-outline-primary': !textOnly,
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
            <i className={classNames(
                'icon-small--arrow-down ms-1',
                {
                    'icon--white': isActive && !iconColour,
                    [`icon--${iconColour}`]: iconColour
                }
            )} />
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
        iconColour: PropTypes.string,
    }),
};