import * as React from 'react';
import PropTypes from 'prop-types';

export function SearchResultTagList({testId, title, tags, children}) {
    return (
        <li
            data-test-id={testId}
            className="search-result__tags-list-row"
        >
            {!title ? null : (
                <span className="search-result__tags-list-row-label">
                    {title}
                </span>
            )}
            {!tags ? null : (
                <div className="tags-list">
                    {tags}
                </div>
            )}
            {children}
        </li>
    );
}

SearchResultTagList.propTypes = {
    testId: PropTypes.string,
    title: PropTypes.string,
    tags: PropTypes.arrayOf(PropTypes.node),
    children: PropTypes.node,
};
