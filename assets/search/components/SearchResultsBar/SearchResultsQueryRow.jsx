import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';
import {SearchResultTagList} from './SearchResultTagList';

export function SearchResultsQueryRow({searchParams, setQuery, refresh}) {
    if (!get(searchParams, 'query.length')) {
        return null;
    }

    return (
        <SearchResultTagList
            title={gettext('Search For')}
            tags={[{
                text: searchParams.query,
                onClick: () => {
                    setQuery('');
                    refresh();
                },
            }]}
        />
    );
}

SearchResultsQueryRow.propTypes = {
    searchParams: PropTypes.object,
    setQuery: PropTypes.func.isRequired,
    refresh: PropTypes.func.isRequired,
};
