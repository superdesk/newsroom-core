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
                <div className="d-contents" key="tags-query">
                    <Tag
                        testId="query-value"
                        text={searchParams.query}
                        onClick={(event) => {
                            event.preventDefault();
                            setQuery('');
                        }}
                    />
                    <span className="search-result__tags-list-row-helper-text">{gettext('in all fields')}</span>
                </div>
            ]}
        />
    );
}

SearchResultsQueryRow.propTypes = {
    searchParams: PropTypes.object,
    setQuery: PropTypes.func.isRequired,
};
