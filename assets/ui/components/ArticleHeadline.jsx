import React from 'react';
import PropTypes from 'prop-types';

export default function ArticleHeadline({item}) {
    return (
        <h2 className='wire-column__preview__headline'>
            {item.es_highlight && item.es_highlight.headline ? (
                <span dangerouslySetInnerHTML={{__html: item.es_highlight.headline[0]}} />
            ) : item.headline ? (
                item.headline
            ) : null}
        </h2>
    );
}

ArticleHeadline.propTypes = {
    item: PropTypes.object.isRequired,
};