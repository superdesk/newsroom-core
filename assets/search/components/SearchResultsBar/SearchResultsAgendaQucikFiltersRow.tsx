import * as React from 'react';
import {gettext} from 'utils';

import {SearchResultTagList} from './SearchResultTagList';
import {Tag} from 'components/Tag';

import {searchFilterSelector} from 'search/selectors';
import {connect} from 'react-redux';
import {clearQuickFilter} from 'search/actions';
import {agendaCoverageStatusFilter, getActiveFilterLabel} from 'agenda/components/AgendaCoverageExistsFilter';
import {setItemTypeFilter} from 'agenda/actions';

interface IReduxStateProps {
    itemTypeFilter?: string;
    activeFilter?: {
        calendar?: any;
        location?: any;
        region?: any;
        coverage_type?: any;
        coverage_status?: any;
    };
}

interface IReduxDispatchProps {
    clearQuickFilter: (filter: string) => void;
    clearItemTypeFilter: () => void;
    clearAllQuickFilters: () => void;
}

type IProps = IReduxDispatchProps & IReduxStateProps;

function SearchResultsAgendaQuickFiltersRow({
    itemTypeFilter,
    activeFilter,
    clearQuickFilter,
    clearItemTypeFilter,
    clearAllQuickFilters,
}: IProps) {
    const pills = [];

    if (itemTypeFilter != null) {
        pills.push(
            <Tag
                key={`tags-filters--from-${itemTypeFilter}`}
                testId="tags-filters--agenda-quick-filters"
                text={itemTypeFilter === 'events' ? gettext('Events Only') : gettext('Planning Only')}
                // readOnly={readonly}
                onClick={(event) => {
                    event.preventDefault();
                    clearItemTypeFilter();
                }}
            />
        );
    }

    if (activeFilter?.['calendar'] != null) {
        pills.push(
            <Tag
                key="tags-filters--calendar"
                testId="tags-filters--agenda-quick-filters-calendar"
                text={activeFilter['calendar']}
                // readOnly={readonly}
                onClick={(event) => {
                    event.preventDefault();
                    clearQuickFilter('calendar');
                }}
            />
        );
    }

    if (activeFilter?.['location'] != null) {
        pills.push(
            <Tag
                key="tags-filters--location"
                testId="tags-filters--agenda-quick-filters-location"
                text={activeFilter['location']}
                // readOnly={readonly}
                onClick={(event) => {
                    event.preventDefault();
                    clearQuickFilter('location');
                }}
            />
        );
    }

    if (activeFilter?.['region'] != null) {
        pills.push(
            <Tag
                key="tags-filters--region"
                testId="tags-filters--agenda-quick-filters-region"
                text={activeFilter['region']}
                // readOnly={readonly}
                onClick={(event) => {
                    event.preventDefault();
                    clearQuickFilter('region');
                }}
            />
        );
    }

    if (activeFilter?.['coverage_type'] != null) {
        pills.push(
            <Tag
                key="tags-filters--coverage_type"
                testId="tags-filters--agenda-quick-filters-coverage_type"
                text={activeFilter['coverage_type']}
                // readOnly={readonly}
                onClick={(event) => {
                    event.preventDefault();
                    clearQuickFilter('coverage_type');
                }}
            />
        );
    }

    if (activeFilter?.['coverage_status'] != null) {
        pills.push(
            <Tag
                key="tags-filters--coverage_status"
                testId="tags-filters--agenda-quick-filters-coverage_status"
                text={getActiveFilterLabel(agendaCoverageStatusFilter, activeFilter)}
                // readOnly={readonly}
                onClick={(event) => {
                    event.preventDefault();
                    clearQuickFilter('coverage_status');
                }}
            />
        );
    }

    if ((pills?.length ?? 0) < 1) {
        return null;
    }

    pills.push(
        <span
            key="tags-filters-separator--clear-1"
            className="tag-list__separator tag-list__separator--blanc"
        />
    );

    pills.push(
        <button
            key="tag-filters--clear-button-1"
            className='nh-button nh-button--tertiary nh-button--small'
            onClick={(event) => {
                event.preventDefault();
                clearAllQuickFilters();
            }}
        >
            {gettext('Clear filters')}
        </button>
    );

    return (
        <SearchResultTagList
            testId="search-results--filters"
            title={gettext('Quick filters applied')}
            tags={pills}
        />
    );
}

const mapStateToProps = (state: any) => ({
    itemTypeFilter: state.agenda.itemType,
    activeFilter: searchFilterSelector(state),
});

const mapDispatchToProps = (dispatch: any) => ({
    clearQuickFilter: (filter: string) => dispatch(clearQuickFilter(filter)),
    clearItemTypeFilter: () => dispatch(setItemTypeFilter(null)),
    clearAllQuickFilters: () => {
        dispatch(setItemTypeFilter(null));
        dispatch(clearQuickFilter());
    }
});


export const SearchResultsAgendaQuickFilters: React.ComponentType =
    connect<IReduxStateProps, IReduxDispatchProps>(mapStateToProps, mapDispatchToProps)(SearchResultsAgendaQuickFiltersRow);
