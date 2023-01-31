import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {gettext} from 'utils';
import DropdownFilterButton from './DropdownFilterButton';

const compareFunction = (a, b) => String(a.key).localeCompare(String(b.key));

export const processBuckets = (buckets, filter, toggleFilter) => (filter.notSorted ? buckets : buckets.sort(compareFunction)).map(
    (bucket, index) =>
        bucket.key === 'divider' ?
            <div className="dropdown-divider" key={index}/> :
            <button
                key={bucket.key}
                className={classNames(
                    'dropdown-item',
                    {'dropdown-item--active': filter.isItemActive && filter.isItemActive(bucket.key)}
                )}
                onClick={() => toggleFilter(filter.field, bucket.key)}
            >{filter.transform ? filter.transform(bucket.key, bucket) : bucket.key}</button>);


function getActiveFilterLabel(filter, activeFilter, isActive) {
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
    buttonProps,
    ...props}) {
    const isActive = !!(activeFilter[filter.field]);
    const filterLabel = getFilterLabel ? getFilterLabel : getActiveFilterLabel;

    return (<div className={classNames(
        'btn-group',
        {[className]: className}
    )} key={filter.field}>
        <DropdownFilterButton
            id={filter.field}
            isActive={isActive}
            autoToggle={props.autoToggle}
            onClick={props.onClick}
            icon={filter.icon}
            label={filterLabel(filter, activeFilter, isActive, {...props})}
            textOnly={(buttonProps || {}).textOnly}
            iconColour={(buttonProps || {}).iconColour}
        />
        <div className='dropdown-menu' aria-labelledby={filter.field}>
            <button
                type='button'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, null)}
            >{gettext(filter.label)}</button>
            <div className='dropdown-divider'></div>
            {getDropdownItems(filter, aggregations, toggleFilter, processBuckets, {...props})}
        </div>
    </div>);
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
    buttonProps: PropTypes.shape({
        textOnly: PropTypes.bool,
        iconColour: PropTypes.string,
    }),
};

export default DropdownFilter;
