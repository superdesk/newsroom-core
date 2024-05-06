import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';
import {gettext} from 'utils';
import {getCoverageStatusText} from 'agenda/utils';

export function CoverageStatus({coverage}: ICoverageMetadataPreviewProps) {
    return (
        <div className='coverage-item__row'>
            <span key="topRow">
                <span key="label" className='coverage-item__text-label me-1'>{gettext('status')}:</span>
                <span key="value">{getCoverageStatusText(coverage)}</span>
            </span>
        </div>
    );
}
