import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import AgendaFilterButton from './AgendaFilterButton';

function AgendaItemTypeFilter ({toggleFilter, itemTypeFilter}) {
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
        <div className="btn-group" key={filter.field}>
            <AgendaFilterButton
                filter={filter}
                activeFilter={activeFilter}
            />
            <div className="dropdown-menu" aria-labelledby={filter.field}>
                <button
                    type="button"
                    className="dropdown-item"
                    onClick={() => toggleFilter(filter.field, null)}
                >
                    {gettext(filter.label)}
                </button>
                <div className="dropdown-divider"></div>
                <button
                    key="events_only"
                    className="dropdown-item"
                    onClick={() => toggleFilter(filter.field, 'events')}
                >
                    {gettext('Events Only')}
                </button>
                <button
                    key="planning_only"
                    className="dropdown-item"
                    onClick={() => toggleFilter(filter.field, 'planning')}
                >
                    {gettext('Planning Only')}
                </button>
            </div>
        </div>
    );
}

AgendaItemTypeFilter.propTypes = {
    toggleFilter: PropTypes.func,
    itemTypeFilter: PropTypes.string,
};


export default AgendaItemTypeFilter;
