import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {gettext} from 'utils';
import {Dropdown} from './Dropdown';

const compareFunction = (a: any, b: any) => String(a.key).localeCompare(String(b.key));

export const processBuckets = (buckets: any, filter: any, toggleFilter: any) => (filter.notSorted ? buckets : buckets.sort(compareFunction)).map(
    (bucket: any, index: any) =>
        bucket.key === 'divider' ?
            <div className="dropdown-divider" key={index}/> :
            <button
                key={bucket.key}
                className={classNames(
                    'dropdown-item',
                    {'dropdown-item--active': filter.isItemActive && filter.isItemActive(bucket.key)}
                )}
                onClick={() => {
                    toggleFilter(filter.field, bucket.key);
                }}
            >{filter.transform ? filter.transform(bucket.key, bucket) : bucket.key}</button>);


function getActiveFilterLabel(filter: any, activeFilter: any, isActive: any) {
    if (isActive) {
        return filter.transform ? filter.transform(activeFilter[filter.field][0]) : gettext(activeFilter[filter.field][0]);
    }
    else {
        return gettext(filter.label);
    }
}

function DropdownFilter({
    aggregations,
    filter,
    toggleFilter,
    activeFilter,
    getDropdownItems,
    getFilterLabel,
    className,
    filterName,
    borderless,
    dropdownMenuHeader,
    resetOptionLabel,
    hideLabelOnMobile,
    ...props
}: any) {
    const isActive = !!(activeFilter[filter.field]);
    const filterLabel = getFilterLabel ? getFilterLabel : getActiveFilterLabel;
    const label = filterLabel(filter, activeFilter, isActive, {...props});
    const items = getDropdownItems(filter, aggregations, toggleFilter, processBuckets, {...props});
    const hasItemsAvailable = (items?.length ?? 0) > 0;

    return (
        <Dropdown
            key={filter.field}
            icon={filter.icon}
            label={label}
            className={className}
            borderless={borderless}
            dropdownMenuHeader={dropdownMenuHeader}
            hideLabelOnMobile={hideLabelOnMobile}
        >
            {(hasItemsAvailable && isActive) && (
                <button
                    type='button'
                    className='dropdown-item'
                    onClick={() => toggleFilter(filter.field, null)}
                >
                    {resetOptionLabel ?? gettext(filter.label)}
                </button>
            )}
            {
                hasItemsAvailable ? items : (
                    <div className='dropdown-item__empty'>
                        {gettext('No {{filterName}} available', {filterName: filterName ?? 'items'})}
                    </div>
                )
            }
        </Dropdown>
    );
}

DropdownFilter.propTypes = {
    aggregations: PropTypes.object,
    filter: PropTypes.object,
    toggleFilter: PropTypes.func,
    activeFilter: PropTypes.object,
    getDropdownItems: PropTypes.func,
    getFilterLabel: PropTypes.func,
    className: PropTypes.string,
    autoToggle: PropTypes.bool,
    onClick: PropTypes.func,
    filterName: PropTypes.string,
    borderless: PropTypes.bool,
    locators: PropTypes.any,
    dropdownMenuHeader: PropTypes.string,
    resetOptionLabel: PropTypes.string,
    hideLabelOnMobile: PropTypes.bool,
};

export default DropdownFilter;
