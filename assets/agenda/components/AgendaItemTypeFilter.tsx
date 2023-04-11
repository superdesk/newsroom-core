import React from 'react';
import {AgendaDropdown} from './AgendaDropdown';
import {gettext} from 'assets/utils';

interface IProps {
    toggleFilter: any;
    itemTypeFilter: string;
    eventsOnlyAccess: boolean;
    restrictCoverageInfo: boolean;
}

function AgendaItemTypeFilter ({toggleFilter, itemTypeFilter, eventsOnlyAccess, restrictCoverageInfo}: IProps) {
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
        icon: 'icon-small--coverage-infographics'
    };

    return (
        <AgendaDropdown key={filter.field}
            filter={filter}
            activeFilter={activeFilter}
            toggleFilter={toggleFilter}
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

export default AgendaItemTypeFilter;
