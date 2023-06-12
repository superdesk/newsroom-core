import React from 'react';
import PropTypes from 'prop-types';

export default function ArticleHeadline({item}: any) {
    return item.headline ? (
        <h2 className="wire-column__preview__headline">
            {item.es_highlight && item.es_highlight.headline ? (
                <span dangerouslySetInnerHTML={{__html: item.es_highlight.headline[0]}} />
            ) : item.headline}
        </h2>
    ) : null;
}

ArticleHeadline.propTypes = {
    item: PropTypes.object.isRequired,
};