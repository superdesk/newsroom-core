import React from 'react';
import classNames from 'classnames';
import {gettext} from 'assets/utils';

const getActiveFilterLabel = (filter: any, activeFilter: any, isActive: boolean) => {
    return isActive ? gettext(activeFilter[filter.field][0]) : gettext(filter.label);
};

interface IProps {
    filter: any;
    activeFilter: any;
    autoToggle: boolean;
    onClick: any;
    getFilterLabel: any;
}

function AgendaFilterButton({filter, activeFilter, autoToggle = true, onClick, getFilterLabel}: IProps) {
    const filterLabel = getFilterLabel ? getFilterLabel : getActiveFilterLabel;
    const isActive = activeFilter[filter.field];
    return (<button
        id={filter.field}
        type='button'
        className={classNames('btn btn-outline-primary btn-sm d-flex align-items-center px-2 ms-2',
            {'active': isActive})}
        data-bs-toggle={autoToggle ? 'dropdown' : undefined}
        aria-haspopup='true'
        aria-expanded='false'
        onClick={onClick} >
        <i className={`${filter.icon} d-md-none`}></i>
        <span className='d-none d-md-block'>{filterLabel(filter, activeFilter, isActive)}</span>
        <i className={classNames('icon-small--arrow-down ms-1', {'icon--white': isActive})}></i>
    </button>);
}

export default AgendaFilterButton;
