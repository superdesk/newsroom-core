import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import {Dropdown} from '../../components/Dropdown';

export function AgendaDropdown({filter, activeFilter, toggleFilter, children}) {

    const isActive = activeFilter[filter.field];

    const getActiveFilterLabel = (filter, activeFilter, isActive) => {
        return isActive ? gettext(activeFilter[filter.field][0]) : gettext(filter.label);
    };

    return (
        <Dropdown
            icon={filter.icon}
            label={getActiveFilterLabel(filter, activeFilter, isActive)}
        >
            <button
                type='button'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, null)}
            >{gettext(filter.label)}</button>
            <div className='dropdown-divider'></div>
            {children}
        </Dropdown>
    );
}

AgendaDropdown.propTypes = {
    children: PropTypes.node,
    filter: PropTypes.object,
    toggleFilter: PropTypes.func,
    activeFilter: PropTypes.object,
};

