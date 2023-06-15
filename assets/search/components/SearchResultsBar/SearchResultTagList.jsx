import * as React from 'react';
import PropTypes from 'prop-types';

import {Tag} from 'components/Tag';

export function SearchResultTagList({title, tags, buttons, children}) {
    return (
        <li className="search-result__tags-list-row">
            {!title ? null : (
                <span className="search-result__tags-list-row-label">
                    {title}
                </span>
            )}
            {!tags ? null : (
                <div className="tags-list">
                    {tags.map((tagProps) => typeof tagProps === 'string' ?
                        <span key={tagProps}>{tagProps}</span> :
                        <Tag
                            key={tagProps.keyValue}
                            {...tagProps}
                        />
                    )}
                </div>
            )}
            {!buttons ? null : (
                <div className="tags-list-row__button-group">
                    {buttons}
                </div>
            )}
            {children}
        </li>
    );
}

SearchResultTagList.propTypes = {
    title: PropTypes.string,
    tags: PropTypes.arrayOf(PropTypes.oneOf([
        PropTypes.string,
        PropTypes.shape(Tag.propTypes),
    ])),
    buttons: PropTypes.arrayOf(PropTypes.node),
    children: PropTypes.node,
};
