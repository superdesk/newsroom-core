import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

function DropdownFilterButton({id, isActive, autoToggle, onClick, icon, label}) {
    return (
        <button
            id={id}
            type="button"
            className={classNames(
                'btn btn-outline-primary btn-sm d-flex align-items-center px-2 ms-2',
                {active: isActive}
            )}
            data-toggle={autoToggle ? 'dropdown' : undefined}
            aria-haspopup='true'
            aria-expanded='false'
            onClick={onClick}
        >
            <i className={`${icon} d-md-none`} />
            <span className="d-none d-md-block">
                {label}
            </span>
            <i className={classNames(
                'icon-small--arrow-down ms-1',
                {'icon--white': isActive}
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
    label: PropTypes.string,
};

DropdownFilterButton.defaultProps = {autoToggle: true};

export default DropdownFilterButton;
