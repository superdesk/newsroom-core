import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';

export function CoverageWireText({wireItems, coverage}: ICoverageMetadataPreviewProps) {
    if (wireItems == null || wireItems.length === 0 || coverage.delivery_id == null) {
        return null;
    }

    const wireItem = wireItems.find((content) => content._id === coverage.delivery_id);

    if (wireItem == null) {
        return null;
    }

    const wireText = wireItem.description_text || wireItem.headline || wireItem.slugline || '';

    return wireText.length === 0 ? null : (
        <div className='coverage-item__row'>
            <p className='wire-articles__item__text m-0'>{wireText}</p>
        </div>
    );
}
