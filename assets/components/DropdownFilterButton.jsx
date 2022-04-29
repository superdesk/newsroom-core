import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import classNames from 'classnames';

const getActiveFilterLabel = (filter, activeFilter, isActive) => {
    if (isActive) {
        return filter.transform ? gettext(filter.transform(activeFilter[filter.field][0])) : gettext(activeFilter[filter.field][0]);
    }
    else {
        return gettext(filter.label);
    }
};

function DropdownFilterButton({filter, activeFilter, autoToggle, onClick, getFilterLabel, ...props}) {
    const isActive = activeFilter[filter.field];
    const filterLabel = getFilterLabel ? getFilterLabel : getActiveFilterLabel;
    return (<button
        id={filter.field}
        type='button'
        className={classNames('btn btn-outline-primary btn-sm d-flex align-items-center px-2 ml-2',
            {'active': isActive})}
        data-toggle={autoToggle ? 'dropdown' : undefined}
        aria-haspopup='true'
        aria-expanded='false'
        onClick={onClick} >
        <i className={`${filter.icon} d-md-none`}></i>
        <span className='d-none d-md-block'>{filterLabel(filter, activeFilter, isActive, {...props})}</span>
        <i className={classNames('icon-small--arrow-down ml-1', {'icon--white': isActive})}></i>
    </button>);
}

DropdownFilterButton.propTypes = {
    filter: PropTypes.object,
    activeFilter: PropTypes.object,
    autoToggle: PropTypes.bool,
    onClick: PropTypes.func,
    getFilterLabel: PropTypes.func,
};

DropdownFilterButton.defaultProps = {autoToggle: true};

export default DropdownFilterButton;
