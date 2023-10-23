import React, {useState} from 'react';
import PropTypes from 'prop-types';
import {get, cloneDeep, uniqBy} from 'lodash';
import {gettext} from 'utils';
import {Skeleton} from 'primereact/skeleton';

import NavGroup from './NavGroup';
import FilterItem from './FilterItem';
import {WithPagination} from 'search/components/WithPagination';

const LIMIT = 5;

const getVisibleBuckets = (
    buckets: Array<any>,
    group: any,
    toggleGroup: (event: any, group: any) => void,
) => {
    if (!buckets.length) {
        return;
    }

    let visibleBuckets = buckets;

    if (buckets.length > LIMIT && !group.isOpen) {
        visibleBuckets = buckets.slice(0, LIMIT).concat([
            <a key={'more'} onClick={(event: any) => toggleGroup(event, group)} className="small" href="">
                {gettext('Show more')}
            </a>
        ]);
    }

    if (buckets.length > LIMIT && group.isOpen) {
        visibleBuckets = buckets.concat([
            <a key={'less'} onClick={(event: any) => toggleGroup(event, group)} className="small" href="">
                {gettext('Show less')}
            </a>
        ]);
    }

    return visibleBuckets;
};


export default function FilterGroup({group, activeFilter, aggregations, toggleFilter, toggleGroup, isLoading}: any) {
    const [searchTerm, setSearchTerm] = useState('');

    if (isLoading === true) {
        return (
            <NavGroup key={group.field} label={group.label}>
                <div className="d-flex align-items-start">
                    <Skeleton size="1rem" className="me-2" />
                    <Skeleton width="8rem" className="mb-2" />
                </div>
                <div className="d-flex align-items-start">
                    <Skeleton size="1rem" className="me-2" />
                    <Skeleton width="13rem" className="mb-2" />
                </div>
                <div className="d-flex align-items-start">
                    <Skeleton size="1rem" className="me-2" />
                    <Skeleton width="8rem" className="mb-2" />
                </div>
            </NavGroup>
        );
    }

    const compareFunction = (a: any, b: any) => group.sorted ? -1 : String(a.key).localeCompare(String(b.key));

    const groupFilter = get(activeFilter, group.field, []);
    const activeBuckets = (get(activeFilter, group.field) || [])
        .map((filter: any) => ({key: filter}));
    const bucketPath = get(group, 'agg_path') || `${group.field}.buckets`;
    const buckets = uniqBy(
        cloneDeep(get(aggregations, bucketPath) || group.buckets || [])
            .concat(activeBuckets),
        'key'
    )
        .sort(compareFunction)
        .filter(({key}: any) => searchTerm.length > 0 ? key.toString().toLocaleLowerCase().includes(searchTerm) : true) as any;

    return (
        <NavGroup key={group.field} label={group.label}>
            <div className="mb-2 search search--small search--with-icon search--bordered m-0">
                <div className="search__form" role="search" aria-label="search">
                    <i className="icon--search icon--muted-2"></i>
                    <input
                        autoComplete='off'
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                        }}
                        value={searchTerm}
                        type="text"
                        name="q"
                        className="search__input form-control"
                        placeholder={gettext('Search Filters')}
                        aria-label={gettext('Search Filters')}
                    />
                    <div className="search__form-buttons">
                        <button className="search__button-clear" aria-label={gettext('Clear search')} type="button">
                            <svg fill="none" height="18" viewBox="0 0 18 18" width="18" xmlns="http://www.w3.org/2000/svg">
                                <path clipRule="evenodd" d="m9 18c4.9706 0 9-4.0294 9-9 0-4.97056-4.0294-9-9-9-4.97056 0-9 4.02944-9 9 0 4.9706 4.02944 9 9 9zm4.9884-12.58679-3.571 3.57514 3.5826 3.58675-1.4126 1.4143-3.58252-3.5868-3.59233 3.5965-1.41255-1.4142 3.59234-3.59655-3.54174-3.54592 1.41254-1.41422 3.54174 3.54593 3.57092-3.57515z" fill="var(--color-text)" fillRule="evenodd" opacity="1"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
            <WithPagination
                key={searchTerm}
                pageSize={10}
                getItems={(pageNo, pageSize) => Promise.resolve({
                    itemCount: buckets?.length ?? 0,
                    items: (buckets ?? []).slice(pageNo === 1 ? 0 : pageNo * pageSize, pageSize),
                })}
            >
                {(items) => (
                    <>
                        {(
                            getVisibleBuckets(items, group, toggleGroup)?.map((item) => (
                                <FilterItem
                                    key={item.key}
                                    bucket={item}
                                    group={group}
                                    toggleFilter={toggleFilter}
                                    groupFilter={groupFilter}
                                />
                            ))
                        )}
                    </>
                )}
            </WithPagination>
        </NavGroup>
    );
}


