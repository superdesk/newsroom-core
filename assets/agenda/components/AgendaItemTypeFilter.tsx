import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import {AgendaDropdown} from './AgendaDropdown';

function AgendaItemTypeFilter ({toggleFilter, itemTypeFilter, eventsOnlyAccess, restrictCoverageInfo}: any) {
    if (eventsOnlyAccess) {
        return null;
    }

    const activeFilter = itemTypeFilter == null ? {} : {
        itemType: [
            itemTypeFilter === 'events' ?
                gettext('Events Only') :
                gettext('Planning Only')
        ]
    };

    const filter: any = {
        label: gettext('Events & Coverages'),
        field: 'itemType',
    };

    return (
        <AgendaDropdown
            key={filter.field}
            filter={filter}
            activeFilter={activeFilter}
            toggleFilter={toggleFilter}
            optionLabel={gettext('Show')}
            resetOptionLabel={gettext('Clear selection')}
            //dropdownMenuHeader={gettext('Item Types')}
            hideLabelOnMobile
        >
            <button
                key="events_only"
                className="dropdown-item"
                onClick={() => toggleFilter(filter.field, 'events')}
            >
                {gettext('Events Only')}
            </button>
            {restrictCoverageInfo ? null : (
                <button
                    key="planning_only"
                    className="dropdown-item"
                    onClick={() => toggleFilter(filter.field, 'planning')}
                >
                    {gettext('Planning Only')}
                </button>
            )}
        </AgendaDropdown>
    );
}

AgendaItemTypeFilter.propTypes = {
    toggleFilter: PropTypes.func,
    itemTypeFilter: PropTypes.string,
    eventsOnlyAccess: PropTypes.bool,
    restrictCoverageInfo: PropTypes.bool,
};


export default AgendaItemTypeFilter;
