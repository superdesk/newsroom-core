import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';

import {SearchResultTagList} from './SearchResultTagList';
import {Tag} from 'components/Tag';


export function SearchResultsQueryRow({searchParams, setQuery}) {
    if (!get(searchParams, 'query.length')) {
        return null;
    }

    return (
        <SearchResultTagList
            testId="search-results--query"
            title={gettext('Search For')}
            tags={[
                <Tag
                    key="tags-query"
                    testId="query-value"
                    text={searchParams.query}
                    onClick={(event) => {
                        event.preventDefault();
                        setQuery('');
                    }}
                />
            ]}
        />
    );
}

SearchResultsQueryRow.propTypes = {
    searchParams: PropTypes.object,
    setQuery: PropTypes.func.isRequired,
};
