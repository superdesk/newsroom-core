import React from 'react';
import PropTypes from 'prop-types';

import {getSlugline} from 'utils';

export default function ArticleSlugline({item}: any) {
    const slugline = getSlugline(item, true);

    return slugline ? (
        <div className="wire-column__preview__slugline">
            {item.es_highlight && item.es_highlight.slugline ? (
                <span dangerouslySetInnerHTML={{__html: item.es_highlight.slugline[0]}} />
            ) : slugline}
        </div>
    ) : null;
}

ArticleSlugline.propTypes = {
    item: PropTypes.object.isRequired,
};
