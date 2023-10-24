import * as React from 'react';
import {gettext, getCreatedSearchParamLabel} from 'utils';

import {SearchResultTagList} from './SearchResultTagList';
import {Tag} from 'components/Tag';

import {IProps as IParentProps} from './SearchResultTagsList';
import {setItemTypeFilter} from 'agenda/actions';
import {clearQuickFilter} from 'search/actions';
import {searchFilterSelector} from 'search/selectors';
import {connect} from 'react-redux';
import {agendaCoverageStatusFilter, getActiveFilterLabel} from 'agenda/components/AgendaCoverageExistsFilter';

const IS_AGENDA = location.pathname.includes('/agenda');

type IProps = Pick<IParentProps,
    'readonly' |
    'searchParams' |
    'filterGroups' |
    'toggleFilter' |
    'setCreatedFilter' |
    'resetFilter'
>;

type IActiveFilter = {
    calendar?: any;
    location?: any;
    region?: any;
    coverage_type?: any;
    coverage_status?: any;
};

type IActiveFilterUnionType = keyof IActiveFilter;

interface IReduxStateProps {
    itemTypeFilter?: string;
    activeFilter?: IActiveFilter;
}

interface IReduxDispatchProps {
    clearQuickFilter: (filter: string) => void;
    clearItemTypeFilter: () => void;
    clearAllQuickFilters: () => void;
}

type IPropsAgendaExtended = IReduxDispatchProps & IReduxStateProps & IProps;

function SearchResultsFiltersRow({
    readonly,
    searchParams,
    filterGroups,
    toggleFilter,
    setCreatedFilter,
    resetFilter,
    itemTypeFilter,
    clearItemTypeFilter,
    activeFilter,
}: IPropsAgendaExtended) {
    const tags = [];

    if (IS_AGENDA) {
        if (itemTypeFilter != null) {
            tags.push(
                <Tag
                    key={`tags-filters--from-${itemTypeFilter}`}
                    testId="tags-filters--agenda-quick-filters"
                    text={itemTypeFilter === 'events' ? gettext('Events Only') : gettext('Planning Only')}
                    readOnly={readonly}
                    onClick={(event) => {
                        event.preventDefault();
                        clearItemTypeFilter();
                    }}
                />
            );
        }

        Object.keys(activeFilter ?? {}).filter((filter) => activeFilter?.[filter as IActiveFilterUnionType] != null)
            .forEach((filter) => {
                tags.push(
                    <Tag
                        key={`tags-filters--${filter}`}
                        testId={`tags-filters--agenda-quick-filters-${filter}`}
                        text={filter === 'coverage_status'
                            ? getActiveFilterLabel(agendaCoverageStatusFilter, activeFilter)
                            :  activeFilter?.[filter as IActiveFilterUnionType]
                        }
                        readOnly={readonly}
                        onClick={(event) => {
                            event.preventDefault();
                            clearQuickFilter(filter);
                        }}
                    />
                );
            });
    }

    if (searchParams.created) {
        const created = getCreatedSearchParamLabel(searchParams.created);

        if (created.relative) {
            tags.push(
                <Tag
                    key="tags-filters--from"
                    testId="tags-filters--created-from"
                    label={gettext('From')}
                    text={created.relative}
                    readOnly={readonly}
                    onClick={(event) => {
                        event.preventDefault();
                        setCreatedFilter({
                            ...searchParams.created,
                            from: null,
                            to: null,
                        });
                    }}
                />
            );
        } else {
            if (created.from) {
                tags.push(
                    <Tag
                        key="tags-filters--from"
                        testId="tags-filters--created-from"
                        label={gettext('From')}
                        text={created.from}
                        readOnly={readonly}
                        onClick={(event) => {
                            event.preventDefault();
                            setCreatedFilter({
                                ...searchParams.created,
                                from: null,
                            });
                        }}
                    />
                );
            }
            if (created.to) {
                tags.push(
                    <Tag
                        key="tags-filters--to"
                        testId="tags-filters--created-to"
                        label={gettext('To')}
                        text={created.to}
                        readOnly={readonly}
                        onClick={(event) => {
                            event.preventDefault();
                            setCreatedFilter({
                                ...searchParams.created,
                                to: null,
                            });
                        }}
                    />
                );
            }
        }
    }

    if (searchParams.filter != null && IS_AGENDA !== true) {
        for (const field in searchParams.filter) {
            const group = filterGroups[field];

            if (!group) {
                // If no group is defined, then this filter is not from
                // the filters tab in the side-panel
                // So we exclude it from the list of tags
                return null;
            }

            searchParams.filter[field].forEach((filterValue: string) => {
                tags.push(
                    <Tag
                        key={`tags-filters--${group.label}--${filterValue}`}
                        // testId={`tags-filters--${group.label}--${filterValue}`}
                        testId={`tags-filters--${group.label}`}
                        label={group.label}
                        text={filterValue}
                        readOnly={readonly}
                        onClick={(event) => {
                            event.preventDefault();
                            toggleFilter(group.field, filterValue, group.single);
                        }}
                    />
                );
            });
        }
    }

    if (!tags.length) {
        return null;
    }

    if (!readonly) {
        tags.push(
            <span
                key="tags-filters-separator--clear"
                className="tag-list__separator tag-list__separator--blanc"
            />
        );
        tags.push(
            <button
                key="tag-filters--clear-button"
                className='nh-button nh-button--tertiary nh-button--small'
                onClick={(event) => {
                    event.preventDefault();
                    resetFilter();
                }}
            >
                {gettext('Clear filters')}
            </button>
        );
    }

    return (
        <SearchResultTagList
            testId="search-results--filters"
            title={gettext('Filters applied')}
            tags={tags}
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

let component: React.ComponentType<IProps> = SearchResultsFiltersRow as React.ComponentType<IProps>;

if (IS_AGENDA) {
    component = connect<IReduxStateProps, IReduxDispatchProps, IProps>(mapStateToProps, mapDispatchToProps)(SearchResultsFiltersRow);
}

export default component;
