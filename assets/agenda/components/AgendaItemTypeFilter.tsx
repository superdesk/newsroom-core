import React from 'react';
import {gettext} from 'utils';
import {AgendaDropdown} from './AgendaDropdown';
import {ItemTypeFilterConfig} from 'interfaces/configs';

interface IProps {
    toggleFilter: (filedName: string, value: string | null) => void;
    itemTypeFilter?: 'events' | 'planning' | 'combined';
    eventsOnlyAccess: boolean;
    restrictCoverageInfo: boolean;
    config?: ItemTypeFilterConfig;
}

function AgendaItemTypeFilter ({toggleFilter, itemTypeFilter, eventsOnlyAccess, restrictCoverageInfo, config}: IProps) {
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

    const filter = {
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
            {config?.events_only === false ? null : (
                <button
                    key="events_only"
                    className="dropdown-item"
                    onClick={() => toggleFilter(filter.field, 'events')}
                >
                    {gettext('Events Only')}
                </button>
            )}
            {restrictCoverageInfo || config?.planning_only === false ? null : (
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

export default AgendaItemTypeFilter;
