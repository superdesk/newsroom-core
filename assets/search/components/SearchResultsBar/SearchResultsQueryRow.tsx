import * as React from 'react';
import {get} from 'lodash';

import {gettext} from 'utils';

import {SearchResultTagList} from './SearchResultTagList';
import {Tag} from 'components/Tag';

import {ISearchParams} from 'interfaces/topic';

interface IProps {
    searchParams: ISearchParams;
    setQuery: (query: string) => void;
    readonly?: boolean;
    refresh?: () => void;
}

export function SearchResultsQueryRow({searchParams, setQuery, readonly, refresh}: IProps) {
    if (!get(searchParams, 'query.length')) {
        return null;
    }

    return (
        <SearchResultTagList
            testId="search-results--query"
            title={gettext('Search For')}
            tags={[
                <div className="d-contents" key="tags-query">
                    <Tag
                        readOnly={readonly === true}
                        testId="query-value"
                        text={searchParams.query ?? ''}
                        onClick={(event) => {
                            event.preventDefault();
                            setQuery('');
                            refresh?.();
                        }}
                    />
                    <span className="search-result__tags-list-row-helper-text">{gettext('in all fields')}</span>
                </div>
            ]}
        />
    );
}
