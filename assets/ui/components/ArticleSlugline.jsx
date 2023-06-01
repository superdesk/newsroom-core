import React from 'react';
import PropTypes from 'prop-types';

import {getSlugline} from 'utils';

export default function ArticleSlugline({item}) {
    const slugline =   item.es_highlight && item.es_highlight.slugline ? <div
        dangerouslySetInnerHTML={({__html: item.es_highlight.slugline[0]})}
    /> : getSlugline(item, true);

    return <span className="wire-column__preview__slug">{slugline}</span>;
}

ArticleSlugline.propTypes = {
    item: PropTypes.object.isRequired,
};
