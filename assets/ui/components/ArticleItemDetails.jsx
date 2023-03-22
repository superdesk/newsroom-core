import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

export default function ArticleItemDetails(props) {
    return (
        <article
            id='preview-article'
            className={classNames(
                'wire-column__preview__content--item-detail-wrap',
                {noselect: props.disableTextSelection}
            )}
        >
            {props.children}
        </article>
    );
}

ArticleItemDetails.propTypes = {
    children: PropTypes.node,
    disableTextSelection: PropTypes.bool,
};

ArticleItemDetails.defaultProps = {disableTextSelection: false};
