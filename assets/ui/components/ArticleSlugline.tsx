import React from 'react';
import PropTypes from 'prop-types';
import {getSlugline} from 'assets/utils';


export default function ArticleSlugline({item}: any) {
    const slugline = getSlugline(item, true);

    return !slugline ? null : (
        <span className="wire-column__preview__slug">{slugline}</span>
    );
}

ArticleSlugline.propTypes = {
    item: PropTypes.object.isRequired,
};
