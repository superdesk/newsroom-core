import React from 'react';
import PropTypes from 'prop-types';

export default function ArticleHeadline({item}) {
    return (
        item.es_highlight && item.es_highlight.headline ? <div
            dangerouslySetInnerHTML={({__html: item.es_highlight.headline[0]})}
        /> : item.headline && <h2 className='wire-column__preview__headline'>{item.headline}</h2> || null
    );
}

ArticleHeadline.propTypes = {
    item: PropTypes.object.isRequired,
};