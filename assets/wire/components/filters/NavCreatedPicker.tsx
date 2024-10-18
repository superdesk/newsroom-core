import React from 'react';
import {gettext} from 'utils';

import NavGroup from './NavGroup';

import {IDateFilter, IDateFilters} from 'interfaces/common';
import {ICreatedFilter} from 'interfaces/search';

interface IProps {
    context: 'wire' | 'agenda';
    createdFilter: ICreatedFilter;
    setCreatedFilter: (createdFilter: ICreatedFilter) => void;
    dateFilters: IDateFilters;
}

function NavCreatedPicker({setCreatedFilter, createdFilter, context, dateFilters}: IProps) {
    const showCustomRange = createdFilter.date_filter === 'custom_date';
    const getFilterValue = (filter: IDateFilter) => context === 'agenda' ? filter.query : filter.filter;

    const onDateFilterChange = (event: {target: {value: string}}) => {
        const value = event.target.value;

        if (value === 'custom_date') {
            setCreatedFilter({...createdFilter, date_filter: value, from: '', to: ''});
        } else {
            if (context === 'agenda') {
                setCreatedFilter({...createdFilter, date_filter: value, from: value, to: undefined});
            } else {
                setCreatedFilter({...createdFilter, date_filter: value, from: undefined, to: undefined});
            }
        }
    };

    const onInputChange = (event: {target: {name: any, value: any}; }) => {
        const newValue = {[event.target.name]: event.target.value};
        setCreatedFilter({...createdFilter, ...newValue});
    };

    return (
        <NavGroup label={context === 'agenda' ? gettext('Event Date') : gettext('Published By')}>
            <div className="formGroup mb-2">
                <select
                    id="date-filter"
                    className="form-control"
                    value={showCustomRange ? 'custom_date' : createdFilter.date_filter || ''}
                    onChange={onDateFilterChange}
                    data-test-id="date-filter-select"
                >
                    {(
                        dateFilters.map((filter) => (
                            <option key={getFilterValue(filter)} value={filter.default ? '' : getFilterValue(filter)}>
                                {filter.name}
                            </option>
                        ))
                    )}
                    <option value="custom_date">{gettext('Custom date range')}</option>
                </select>
            </div>
            {showCustomRange && (
                <>
                    <div className="formGroup mb-2">
                        <label htmlFor="created-from">{gettext('From')}</label>
                        <input
                            id="created-from"
                            type="date"
                            name="from"
                            className="form-control"
                            onChange={onInputChange}
                            value={createdFilter.from || ''}
                            data-test-id="custom-date-from"
                        />
                    </div>
                    <div className="formGroup">
                        <label htmlFor="created-to">{gettext('To')}</label>
                        <input
                            id="created-to"
                            type="date"
                            name="to"
                            className="form-control"
                            onChange={onInputChange}
                            value={createdFilter.to || ''}
                            data-test-id="custom-date-to"
                        />
                    </div>
                </>
            )}
        </NavGroup>
    );
}

export default NavCreatedPicker;
