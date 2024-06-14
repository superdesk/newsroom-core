import React, {useState} from 'react';
import {get, cloneDeep, uniqBy} from 'lodash';
import {getConfig, gettext} from 'utils';
import {Skeleton} from 'primereact/skeleton';

import NavGroup from './NavGroup';
import FilterItem from './FilterItem';
import {WithPagination} from 'components/pagination/WithPagination';
import {searchIcon} from 'search/components/search-icon';

/**
 * If the filter count is less than 50 we
 * shouldn't render the search.
 */
const SEARCHBAR_THRESHOLD = getConfig('searchbar_threshold_value') || 50;
const LIMIT = 5;
type IBucket = {key: string, doc_count: string};

const getVisibleBuckets = (
    buckets: Array<JSX.Element>,
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
    const activeBuckets: Array<any> = (get(activeFilter, group.field) || [])
        .map((filter: any) => ({key: filter}));
    const bucketPath: string = get(group, 'agg_path') || `${group.field}.buckets`;
    const allBuckets = uniqBy(
        cloneDeep(get(aggregations, bucketPath) || group.buckets || []).concat(activeBuckets) as Array<IBucket>,
        'key',
    );
    const bucketsBySearchTerm = allBuckets
        .filter(({key}: any) => searchTerm.length > 0
            ? key.toString().toLocaleLowerCase().includes(searchTerm.toLocaleLowerCase())
            : true,
        )
        .sort(compareFunction);

    return (
        <NavGroup key={group.field} label={group.label}>
            {allBuckets.length > SEARCHBAR_THRESHOLD && (
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
                            className="search__input form-control"
                            placeholder={gettext('Search Filters')}
                            aria-label={gettext('Search Filters')}
                        />
                        <div className="search__form-buttons">
                            <button className="search__button-clear" aria-label={gettext('Clear search')} type="button">
                                {searchIcon}
                            </button>
                        </div>
                    </div>
                </div>
            )}
            <WithPagination
                style='bottom-only'
                key={searchTerm}
                pageSize={50}
                getItems={(pageNo, pageSize) => {
                    const step = pageNo === 1 ? 0 : (pageNo - 1) * pageSize;

                    return Promise.resolve({
                        itemCount: bucketsBySearchTerm?.length ?? 0,
                        items: (bucketsBySearchTerm ?? []).slice(step, pageSize + step),
                    });
                }}
            >
                {(items: Array<IBucket>) => {
                    const itemsJsx = items.map((item) => (
                        <FilterItem
                            key={item.key}
                            bucket={item}
                            group={group}
                            toggleFilter={toggleFilter}
                            groupFilter={groupFilter}
                        />
                    ));

                    return <div className='mb-1 mt-1' >{getVisibleBuckets(itemsJsx, group, toggleGroup)}</div>;
                }}
            </WithPagination>
        </NavGroup>
    );
}


