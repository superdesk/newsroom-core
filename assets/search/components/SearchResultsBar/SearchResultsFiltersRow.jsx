import * as React from 'react';
import PropTypes from 'prop-types';

import {gettext, getCreatedSearchParamLabel} from 'utils';

import {SearchResultTagList} from './SearchResultTagList';
import {Tag} from 'components/Tag';

export function SearchResultsFiltersRow({searchParams, filterGroups, toggleFilter, setCreatedFilter, resetFilter, refresh}) {
    const tags = [];

    if (searchParams.created) {
        const created = getCreatedSearchParamLabel(searchParams.created);

        if (created.relative) {
            tags.push(
                <Tag
                    key="tags-filters--from"
                    label={gettext('From')}
                    text={created.relative}
                    onClick={() => {
                        setCreatedFilter({
                            ...searchParams.created,
                            from: null,
                            to: null,
                        });
                        refresh();
                    }}
                />
            );
        } else {
            if (created.from) {
                tags.push(
                    <Tag
                        key="tags-filters--from"
                        label={gettext('From')}
                        text={created.from}
                        onClick={() => {
                            setCreatedFilter({
                                ...searchParams.created,
                                from: null,
                            });
                            refresh();
                        }}
                    />
                );
            }
            if (created.to) {
                tags.push(
                    <Tag
                        key="tags-filters--to"
                        label={gettext('To')}
                        text={created.to}
                        onClick={() => {
                            setCreatedFilter({
                                ...searchParams.created,
                                to: null,
                            });
                            refresh();
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
                        label={group.label}
                        text={filterValue}
                        onClick={() => {
                            toggleFilter(group.field, filterValue, group.single);
                            refresh();
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
            onClick={() => {
                resetFilter();
                refresh();
            }}
        >
            {gettext('Clear filters')}
        </button>
    );

    return (
        <SearchResultTagList
            title={gettext('Filters applied')}
            tags={tags}
            // buttons={[
            //     <button
            //         key="clear_filters_button"
            //         className="nh-button nh-button--secondary btn-responsive btn--small"
            //         onClick={() => {
            //             resetFilter();
            //             refresh();
            //         }}
            //     >
            //         {gettext('Clear filters')}
            //     </button>
            // ]}
        />
    );
}

SearchResultsFiltersRow.propTypes = {
    searchParams: PropTypes.object,
    filterGroups: PropTypes.object,
    toggleFilter: PropTypes.func.isRequired,
    setCreatedFilter: PropTypes.func.isRequired,
    resetFilter: PropTypes.func.isRequired,
    refresh: PropTypes.func.isRequired,
};
