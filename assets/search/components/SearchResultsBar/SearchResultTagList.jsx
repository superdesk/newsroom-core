import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

export function SearchResultTagList({testId, title, tags, children, secondary}) {
    return (
        <li
            data-test-id={testId}
            className={classNames(
                'search-result__tags-list-row',
                {'search-result__tags-list-row--secondary': secondary},
            )}
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
    secondary: PropTypes.bool,
    testId: PropTypes.string,
    title: PropTypes.string,
    tags: PropTypes.arrayOf(PropTypes.node),
    children: PropTypes.node,
};
