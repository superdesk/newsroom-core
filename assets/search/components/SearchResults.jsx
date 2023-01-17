import React from 'react';
import PropTypes from 'prop-types';

import {gettext} from 'utils';

const SearchResults = ({totalItems, totalItemsLabel}) => (
    <div className="search-results__main-header d-flex mt-0 px-3 align-items-center">
        <div className="d-flex flex-column flex-md-row h-100">
            <div className="navbar-text search-results-info">
                <span className="search-results-info__num">
                    {totalItems}
                </span>
                <span className="search-results-info__text flex-column">
                    {!totalItemsLabel ? (
                        <span>{gettext('search results found')}</span>
                    ) : (
                        <React.Fragment>
                            <span>{gettext('search results for:')}</span>
                            <span className="text-break"><b>{totalItemsLabel}</b></span>
                        </React.Fragment>
                    )}
                </span>
            </div>
        </div>
    </div>
);

SearchResults.propTypes = {
    totalItems: PropTypes.number,
    totalItemsLabel: PropTypes.string,
};

export default SearchResults;
