import * as React from 'react';
import PropTypes from 'prop-types';

import {gettext, getCreatedSearchParamLabel} from 'utils';

import {SearchResultTagList} from './SearchResultTagList';
import {Tag} from 'components/Tag';

export function SearchResultsFiltersRow({searchParams, filterGroups, toggleFilter, setCreatedFilter, resetFilter}) {
    const tags = [];

    if (searchParams.created) {
        const created = getCreatedSearchParamLabel(searchParams.created);

        if (created.relative) {
            tags.push(
                <Tag
                    key="tags-filters--from"
                    testId="tags-filters--created-from"
                    label={gettext('From')}
                    text={created.relative}
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

    if (searchParams.filter) {
        Object.keys(searchParams.filter).forEach((field) => {
            const group = filterGroups[field];

            if (!group) {
                // If no group is defined, then this filter is not from
                // the filters tab in the side-panel
                // So we exclude it from the list of tags
                return;
            }

            searchParams.filter[field].forEach((filterValue) => {
                tags.push(
                    <Tag
                        key={`tags-filters--${group.label}--${filterValue}`}
                        // testId={`tags-filters--${group.label}--${filterValue}`}
                        testId={`tags-filters--${group.label}`}
                        label={group.label}
                        text={filterValue}
                        onClick={(event) => {
                            event.preventDefault();
                            toggleFilter(group.field, filterValue, group.single);
                        }}
                    />
                );
            });
        });
    }

    if (!tags.length) {
        return null;
    }

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

    return (
        <SearchResultTagList
            testId="search-results--filters"
            title={gettext('Filters applied')}
            tags={tags}
        />
    );
}

SearchResultsFiltersRow.propTypes = {
    searchParams: PropTypes.object,
    filterGroups: PropTypes.object,
    toggleFilter: PropTypes.func.isRequired,
    setCreatedFilter: PropTypes.func.isRequired,
    resetFilter: PropTypes.func.isRequired,
};
