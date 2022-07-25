import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {gettext} from 'utils';
import AgendaTypeAheadFilter from './AgendaTypeAheadFilter';
import DropdownFilter from '../../components/DropdownFilter';
import {getCoverageDisplayName, groupRegions, getRegionName} from '../utils';
import AgendaCoverageExistsFilter from './AgendaCoverageExistsFilter';
import AgendaItemTypeFilter from './AgendaItemTypeFilter';

import {AgendaCalendarAgendaFilter} from './AgendaCalendarAgendaFilter';


export const transformFilterBuckets = (filter, aggregations, props) => {
    if (!filter.transformBuckets) {
        return aggregations[filter.field].buckets;
    }

    return filter.transformBuckets(filter, aggregations, props);
};

const filters = [{
    label: gettext('Any location'),
    field: 'location',
    typeAhead: true,
    icon: 'icon-small--location',
    itemTypes: ['events', 'combined'],
}, {
    label: gettext('Any region'),
    field: 'place',
    icon: 'icon-small--region',
    itemTypes: ['events', 'combined'],
    transformBuckets: groupRegions,
    notSorted: true,
    transform: getRegionName,
    getFilterLabel: (filter, activeFilter, isActive, props) => {
        if (!isActive) {
            return filter.label;
        }

        let region;
        if (get(activeFilter, `${filter.field}[0]`) && props.locators) {
            region = (Object.values(props.locators) || []).find((l) => l.name === get(activeFilter, `${filter.field}[0]`));
        }

        return region ? (get(region, 'state') || get(region, 'country') || get(region, 'world_region')) : get(activeFilter, `${filter.field}[0]`);
    }
}, {
    label: gettext('Any coverage type'),
    field: 'coverage',
    nestedField: 'coverage_type',
    icon: 'icon-small--coverage-text',
    transform: getCoverageDisplayName,
    itemTypes: ['planning', 'combined'],
}];


export const getDropdownItems = (filter, aggregations, toggleFilter, processBuckets, props) => {
    if (!filter.nestedField && aggregations && aggregations[filter.field]) {
        return processBuckets(transformFilterBuckets(filter, aggregations, props), filter, toggleFilter);
    }

    if (filter.nestedField && aggregations && aggregations[filter.field] && aggregations[filter.field][filter.nestedField]) {
        return processBuckets(aggregations[filter.field][filter.nestedField].buckets, filter, toggleFilter);
    }

    return [];
};

function AgendaFilters({aggregations, toggleFilter, activeFilter, eventsOnlyAccess, itemTypeFilter, locators}) {
    const displayFilters = filters.filter(
        (filter) => filter.itemTypes.includes(itemTypeFilter || 'combined')
    );

    return (<div className='wire-column__main-header-agenda d-flex m-0 px-3 align-items-center flex-wrap flex-sm-nowrap'>
        <AgendaCalendarAgendaFilter
            aggregations={aggregations}
            activeFilter={activeFilter}
            toggleFilter={toggleFilter}
            itemTypeFilter={itemTypeFilter}
        />

        {displayFilters.map((filter) => (
            filter.typeAhead ? <AgendaTypeAheadFilter
                key={filter.label}
                aggregations={aggregations}
                filter={filter}
                toggleFilter={toggleFilter}
                activeFilter={activeFilter}
                getDropdownItems={getDropdownItems}
            /> : <DropdownFilter
                key={filter.label}
                aggregations={aggregations}
                filter={filter}
                toggleFilter={toggleFilter}
                activeFilter={activeFilter}
                getDropdownItems={getDropdownItems}
                locators={locators}
                getFilterLabel={filter.getFilterLabel}
            />
        ))}
        {!eventsOnlyAccess && itemTypeFilter !== 'events' && (
            <AgendaCoverageExistsFilter
                activeFilter={activeFilter}
                toggleFilter={toggleFilter}
            />
        )}
        {!eventsOnlyAccess && (
            <AgendaItemTypeFilter
                activeFilter={activeFilter}
                itemTypeFilter={itemTypeFilter}
                toggleFilter={toggleFilter}
            />
        )}
    </div>);
}

AgendaFilters.propTypes = {
    aggregations: PropTypes.object,
    toggleFilter: PropTypes.func,
    activeFilter: PropTypes.object,
    eventsOnlyAccess: PropTypes.bool,
    itemTypeFilter: PropTypes.string,
    locators: PropTypes.arrayOf(PropTypes.object),
};

export default AgendaFilters;
