import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import {AgendaDropdown} from './AgendaDropdown';

const filter = {
    label: gettext('Any coverage status'),
    field: 'coverage_status',
    nestedField: 'coverage_status',
    icon: 'icon-small--coverage-unrecognized',
};

function AgendaCoverageExistsFilter ({toggleFilter, activeFilter}) {
    return (
        <AgendaDropdown
            filter={filter}
            activeFilter={activeFilter}
            toggleFilter={toggleFilter}
            getFilterLabel={getActiveFilterLabel}
        >
            <button
                key='coverage-planned'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, 'planned')}
            >{gettext('Coverage is planned')}
            </button>
            <button
                key='coverage-not-planned'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, 'not planned')}
            >{gettext('Coverage not planned')}
            </button>
        </AgendaDropdown>
    );
}

AgendaCoverageExistsFilter.propTypes = {
    toggleFilter: PropTypes.func,
    activeFilter: PropTypes.object,
};

export default AgendaCoverageExistsFilter;