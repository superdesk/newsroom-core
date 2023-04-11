import React from 'react';
import {AgendaDropdown} from './AgendaDropdown';

const compareFunction = (a: any, b: any) => String(a.key).localeCompare(String(b.key));

const processBuckets = (
    buckets: Array<any>,
    filter: any,
    toggleFilter: any,
) => buckets.sort(compareFunction).map((bucket) => (
    <button
        key={bucket.key}
        className='dropdown-item'
        onClick={() => toggleFilter(filter.field, bucket.key)}
    >
        {filter.transform ? filter.transform(bucket.key) : bucket.key}
    </button>
));

interface IProps {
    aggregations: any;
    filter: any;
    toggleFilter: any;
    activeFilter: any;
    getDropdownItems: any;
}

function AgendaDropdownFilter({aggregations, filter, toggleFilter, activeFilter, getDropdownItems}: IProps) {
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

export default AgendaDropdownFilter;
