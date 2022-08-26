import React from 'react';
import PropTypes from 'prop-types';
import {uniqBy} from 'lodash';

import PreviewTagsLink from './PreviewTagsLink';


export function PreviewTagsLinkList({urlPrefix, items, field}) {
    return items == null || (items.length || 0) === 0 ? null : (
        uniqBy(items, 'code').map((item) => (
            <PreviewTagsLink
                key={item.code}
                href={urlPrefix + encodeURIComponent(JSON.stringify({[field]: [item.name]}))}
                text={item.name}
            />
        ))
    );
}

PreviewTagsLinkList.propTypes = {
    urlPrefix: PropTypes.string,
    items: PropTypes.array,
    field: PropTypes.string,
};
