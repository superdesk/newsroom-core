import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {gettext} from 'utils';
import {Dropdown} from 'bootstrap';

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
    const dropdown = React.useRef();

    React.useEffect(() => {
        const dropdownInstance = Dropdown.getOrCreateInstance(dropdown.current, {autoClose: true});

        return () => {
            dropdownInstance.hide();
        };
    });

    const icon= filter.icon;
    const label = filterLabel(filter, activeFilter, isActive, {...props});
    const textOnly = (buttonProps || {}).textOnly;
    const iconColour= (buttonProps || {}).iconColour;

    return (<div className={classNames(
        'dropdown',
        'btn-group',
        {[className]: className}
    )} key={filter.field}>
        <button
            id={filter.field}
            type="button"
            className={classNames(
                'btn btn-sm d-flex align-items-center px-2 ms-2 dropdown-toggle',
                {
                    active: isActive,
                    'btn-text-only': textOnly,
                    'btn-outline-primary': !textOnly,
                }
            )}
            data-bs-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
            onClick={props.onClick}
            ref={dropdown}
        >
            {!icon ? null : (
                <i className={`${icon} d-md-none`} />
            )}
            {textOnly ? label : (
                <span className="d-none d-md-block">
                    {label}
                </span>
            )}
            <i className={classNames(
                'icon-small--arrow-down ms-1',
                {
                    'icon--white': isActive && !iconColour,
                    [`icon--${iconColour}`]: iconColour
                }
            )} />
        </button>
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
