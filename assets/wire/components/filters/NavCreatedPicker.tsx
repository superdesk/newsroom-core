import React, {useState, useEffect} from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';

import NavGroup from './NavGroup';
import {isEmpty} from 'lodash';

const agendaShortcuts = [
    {label: gettext('Today'), value: 'now/d'},
    {label: gettext('This week'), value: 'now/w'},
    {label: gettext('This month'), value: 'now/M'},
];

function NavCreatedPicker({setCreatedFilter, createdFilter, context, wireFilters}: any) {
    const [showCustomRange, setShowCustomRange] = useState(false);

    useEffect(() => {
        if (createdFilter.date_filter === 'custom_date') {
            setShowCustomRange(true);
        } else {
            setShowCustomRange(false);
        }
        if (isEmpty(createdFilter) && context == 'wire'){
            const defaultFilter = wireFilters.find((filter: {default: any}) => filter.default);
            setCreatedFilter({...createdFilter, date_filter: defaultFilter.filter});
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
                >
                    {context === 'agenda' ? (
                        agendaShortcuts.map((shortcut) => (
                            <option key={shortcut.value} value={shortcut.value}>
                                {shortcut.label}
                            </option>
                        ))
                    ) : (
                        wireFilters.map((filter: {filter: string, name: string}) => (
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
    wireFilters: PropTypes.array,
};

export default NavCreatedPicker;
