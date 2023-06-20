import React from 'react';
import PropTypes from 'prop-types';
import {AgendaDropdown} from './AgendaDropdown';

const compareFunction = (a: any, b: any) => String(a.key).localeCompare(String(b.key));

const processBuckets = (buckets: any, filter: any, toggleFilter: any) => buckets.sort(compareFunction).map((bucket: any) =>
    <button
        key={bucket.key}
        className='dropdown-item'
        onClick={() => toggleFilter(filter.field, bucket.key)}
    >{filter.transform ? filter.transform(bucket.key) : bucket.key}</button>);

function AgendaDropdownFilter({aggregations, filter, toggleFilter, activeFilter, getDropdownItems}: any) {
    return (
        <AgendaDropdown
            filter={filter}
            activeFilter={activeFilter}
            toggleFilter={toggleFilter}
        >
            {getDropdownItems(filter, aggregations, toggleFilter, processBuckets)}
        </AgendaDropdown>
    );
}

AgendaDropdownFilter.propTypes = {
    aggregations: PropTypes.object,
    filter: PropTypes.object,
    toggleFilter: PropTypes.func,
    activeFilter: PropTypes.object,
    getDropdownItems: PropTypes.func,
};

export default AgendaDropdownFilter;
