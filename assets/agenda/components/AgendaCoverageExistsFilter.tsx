import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';
import {AgendaDropdown} from './AgendaDropdown';

const filter = {
    label: gettext('Any coverage status'),
    field: 'coverage_status',
    nestedField: 'coverage_status',
};

const FILTER_VALUES = {
    PLANNED: 'planned',
    NOT_PLANNED: 'not planned',
    MAY_BE: 'may be',
    COMPLETED: 'completed'
};

function getActiveFilterLabel(filter: any, activeFilter: any) {
    const filterValue = get(activeFilter, `${filter.field}[0]`);

    switch (filterValue) {
    case FILTER_VALUES.PLANNED:
        return gettext('Planned');
    case FILTER_VALUES.NOT_PLANNED:
        return gettext('Not Planned');
    case FILTER_VALUES.MAY_BE:
        return gettext('Not Decided');
    case FILTER_VALUES.COMPLETED:
        return gettext('Completed');
    }

    return filter.label;
}

function AgendaCoverageExistsFilter ({toggleFilter, activeFilter}: any) {
    return (
        <AgendaDropdown
            filter={filter}
            activeFilter={activeFilter}
            toggleFilter={toggleFilter}
            getFilterLabel={getActiveFilterLabel}
            optionLabel={gettext('Coverage')}
        >
            <button
                key='coverage-planned'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, FILTER_VALUES.PLANNED)}
            >{gettext('Coverage is planned')}
            </button>
            <button
                key='coverage-not-planned'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, FILTER_VALUES.NOT_PLANNED)}
            >{gettext('Coverage not planned')}
            </button>
            <button
                key='coverage-not-decided'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, FILTER_VALUES.MAY_BE)}
            >{gettext('Coverage not decided')}
            </button>
            <button
                key='coverage-completed'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, FILTER_VALUES.COMPLETED)}
            >{gettext('Coverage completed')}
            </button>
        </AgendaDropdown>
    );
}

AgendaCoverageExistsFilter.propTypes = {
    toggleFilter: PropTypes.func,
    activeFilter: PropTypes.object,
};

export default AgendaCoverageExistsFilter;
