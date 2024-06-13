import React, {useState, useEffect} from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';

import NavGroup from './NavGroup';
import {isEmpty} from 'lodash';

function NavCreatedPicker({setCreatedFilter, createdFilter, context, dateFilters}: any) {
    const [showCustomRange, setShowCustomRange] = useState(createdFilter.date_filter === 'custom_date');

    useEffect(() => {
        setShowCustomRange(createdFilter.date_filter === 'custom_date');
        if (isEmpty(createdFilter) && context === 'wire'){
            const defaultFilter = dateFilters.find((filter: {default: any}) => filter.default);
            setCreatedFilter({...createdFilter, date_filter: defaultFilter?.filter});
        }
    }, [createdFilter.date_filter]);

    const onDateFilterChange = (event: {target: {value: any}}) => {
        const value = event.target.value;
        if (value === 'custom_date') {
            setShowCustomRange(true);
            setCreatedFilter({...createdFilter, date_filter: value, from: '', to: ''});
        } else {
            setShowCustomRange(false);
            if (context === 'agenda') {
                setCreatedFilter({...createdFilter, date_filter: value, from: value, to: null});
            } else {
                setCreatedFilter({...createdFilter, date_filter: value, from: null, to: null});
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
                    {context === 'agenda' ? (
                        dateFilters.map((filter: {query: string, name: string}) => (
                            <option key={filter.query} value={filter.query}>
                                {filter.name}
                            </option>
                        ))
                    ) : (
                        dateFilters.map((filter: {filter: string, name: string}) => (
                            <option key={filter.filter} value={filter.filter}>
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

NavCreatedPicker.propTypes = {
    createdFilter: PropTypes.object.isRequired,
    setCreatedFilter: PropTypes.func.isRequired,
    context: PropTypes.string,
    dateFilters: PropTypes.array,
};

export default NavCreatedPicker;
