import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';
import AgendaFilterButton from './AgendaFilterButton';

const filter = {
    label: gettext('Any coverage status'),
    field: 'coverage_status',
    nestedField: 'coverage_status',
    icon: 'icon-small--coverage-unrecognized',
};

const FILTER_VALUES = {
    PLANNED: 'planned',
    NOT_PLANNED: 'not planned',
};

function getActiveFilterLabel(filter, activeFilter) {
    const filterValue = get(activeFilter, `${filter.field}[0]`);

    switch (filterValue) {
    case FILTER_VALUES.PLANNED:
        return gettext('Planned');
    case FILTER_VALUES.NOT_PLANNED:
        return gettext('Not Planned');
    }

    return filter.label;
}

function AgendaCoverageExistsFilter ({toggleFilter, activeFilter}) {
    return (<div className="btn-group" key={filter.field}>
        <AgendaFilterButton
            filter={filter}
            activeFilter={activeFilter}
            getFilterLabel={getActiveFilterLabel}
        />
        <div className='dropdown-menu' aria-labelledby={filter.field}>
            <button
                type='button'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, null)}
            >{gettext(filter.label)}</button>
            <div className='dropdown-divider'></div>
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
        </div>
    </div>);
}

AgendaCoverageExistsFilter.propTypes = {
    toggleFilter: PropTypes.func,
    activeFilter: PropTypes.object,
};


export default AgendaCoverageExistsFilter;
