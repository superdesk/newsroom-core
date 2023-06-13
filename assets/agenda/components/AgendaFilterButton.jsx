import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import classNames from 'classnames';

const getActiveFilterLabel = (filter, activeFilter, isActive) => {
    return isActive ? gettext(activeFilter[filter.field][0]) : gettext(filter.label);
};

function AgendaFilterButton({filter, activeFilter, autoToggle, onClick, getFilterLabel}) {
    const filterLabel = getFilterLabel ? getFilterLabel : getActiveFilterLabel;
    const isActive = activeFilter[filter.field];
    return (<button
        id={filter.field}
        type='button'
        className={classNames('nh-dropdown-button ms-2',{' nh-dropdown-button--active': isActive})}
        data-bs-toggle={autoToggle ? 'dropdown' : undefined}
        aria-haspopup='true'
        aria-expanded='false'
        onClick={onClick} >
        <i className={`${filter.icon} d-md-none`}></i>
        <span className='d-none d-md-block'>{filterLabel(filter, activeFilter, isActive)}</span>
        <i className='icon-small--arrow-down'></i>
    </button>);
}

AgendaFilterButton.propTypes = {
    filter: PropTypes.object,
    activeFilter: PropTypes.object,
    autoToggle: PropTypes.bool,
    onClick: PropTypes.func,
    getFilterLabel: PropTypes.func,
};

AgendaFilterButton.defaultProps = {autoToggle: true};

export default AgendaFilterButton;
