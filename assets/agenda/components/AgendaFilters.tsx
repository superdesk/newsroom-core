import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {gettext} from 'utils';
import {getCoverageDisplayName, groupRegions, getRegionName} from '../utils';
import {agendaFiltersConfigSelector} from '../selectors';

import DropdownFilter from '../../components/DropdownFilter';
import AgendaCoverageExistsFilter from './AgendaCoverageExistsFilter';
import AgendaItemTypeFilter from './AgendaItemTypeFilter';
import {AgendaCalendarAgendaFilter} from './AgendaCalendarAgendaFilter';
import {LocationFilter} from './LocationFilter';

export const transformFilterBuckets = (filter: any, aggregations: any, props: any) => {
    if (!filter.transformBuckets) {
        return aggregations[filter.field].buckets;
    }

    return filter.transformBuckets(filter, aggregations, props);
};

const renderFilter: any = {
    item_type: (props: any) => (
        <AgendaItemTypeFilter
            key="item_type"
            itemTypeFilter={props.itemTypeFilter}
            toggleFilter={props.toggleFilter}
            eventsOnlyAccess={props.eventsOnlyAccess}
            restrictCoverageInfo={props.restrictCoverageInfo}
        />
    ),
    calendar: (props: any) => (
        <AgendaCalendarAgendaFilter
            key="calendar"
            aggregations={props.aggregations}
            activeFilter={props.activeFilter}
            toggleFilter={props.toggleFilter}
            itemTypeFilter={props.itemTypeFilter}
        />
    ),
    location: (props: any) => (
        !['events', 'combined'].includes(props.itemTypeFilter || 'combined') ? null : (
            <LocationFilter
                key="location"
                activeFilter={props.activeFilter}
                toggleFilter={props.toggleFilter}
            />
        )
    ),
    region: (props: any) => (
        !['events', 'planning', 'combined'].includes(props.itemTypeFilter || 'combined') ? null : (
            <DropdownFilter
                key="region"
                filterName={gettext('Regions')}
                aggregations={props.aggregations}
                toggleFilter={props.toggleFilter}
                activeFilter={props.activeFilter}
                getDropdownItems={getDropdownItems}
                locators={props.locators}
                dropdownMenuHeader={gettext('Regions')}
                resetOptionLabel={gettext('Clear selection')}
                getFilterLabel={(filter: any, activeFilter: any, isActive: any, props: any) => {
                    if (!isActive) {
                        return filter.label;
                    }

                    let region: any;
                    if (get(activeFilter, `${filter.field}[0]`) && props.locators) {
                        region = (Object.values(props.locators) || []).find((l: any) => l.name === get(activeFilter, `${filter.field}[0]`));
                    }

                    return region ? (get(region, 'state') || get(region, 'country') || get(region, 'world_region')) : get(activeFilter, `${filter.field}[0]`);
                }}
                filter={{
                    label: gettext('Region'),
                    field: 'place',
                    itemTypes: ['events', 'combined'],
                    transformBuckets: groupRegions,
                    notSorted: true,
                    transform: getRegionName,
                }}
            />
        )
    ),
    coverage_type: (props: any) => (
        !['planning', 'combined'].includes(props.itemTypeFilter || 'combined') ? null : (
            <DropdownFilter
                filterName={gettext('Coverage types')}
                key="coverage_type"
                aggregations={props.aggregations}
                toggleFilter={props.toggleFilter}
                activeFilter={props.activeFilter}
                getDropdownItems={getDropdownItems}
                dropdownMenuHeader={gettext('Coverage types')}
                resetOptionLabel={gettext('Clear selection')}
                hideLabelOnMobile={true}
                filter={{
                    label: gettext('Coverage type'),
                    field: 'coverage',
                    nestedField: 'coverage_type',
                    transform: getCoverageDisplayName,
                }}
            />
        )
    ),
    coverage_status: (props: any) => (
        (props.eventsOnlyAccess || props.itemTypeFilter === 'events') ? null : (
            <AgendaCoverageExistsFilter
                key="coverage_status"
                activeFilter={props.activeFilter}
                toggleFilter={props.toggleFilter}
            />
        )
    ),
};

export function getDropdownItems(filter: any, aggregations: any, toggleFilter: any, processBuckets: any, props: any) {
    if (!filter.nestedField && aggregations && aggregations[filter.field]) {
        return processBuckets(transformFilterBuckets(filter, aggregations, props), filter, toggleFilter);
    }

    if (filter.nestedField && aggregations && aggregations[filter.field] && aggregations[filter.field][filter.nestedField]) {
        return processBuckets(aggregations[filter.field][filter.nestedField].buckets, filter, toggleFilter);
    }

    return [];
}

function AgendaFiltersComponent(props: any) {
    return (
        <div className='navbar navbar--flex navbar--quick-filter'>
            {props.filtersConfig.map((filterName: any) => (
                renderFilter[filterName](props)
            ))}
        </div>
    );
}

AgendaFiltersComponent.propTypes = {
    aggregations: PropTypes.object,
    toggleFilter: PropTypes.func,
    activeFilter: PropTypes.object,
    eventsOnlyAccess: PropTypes.bool,
    restrictCoverageInfo: PropTypes.bool,
    itemTypeFilter: PropTypes.string,
    locators: PropTypes.arrayOf(PropTypes.object),
    filtersConfig: PropTypes.arrayOf(PropTypes.string),
};

const mapStateToProps = (state: any) => ({
    filtersConfig: agendaFiltersConfigSelector(state),
});

const AgendaFilters: React.ComponentType<any> = connect(mapStateToProps)(AgendaFiltersComponent);

export default AgendaFilters;
