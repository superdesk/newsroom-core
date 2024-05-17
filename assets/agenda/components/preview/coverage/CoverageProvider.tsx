import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';
import {gettext} from 'utils';

export function CoverageProvider({coverage}: ICoverageMetadataPreviewProps) {
    return coverage.coverage_provider == null ? null : (
        <div className='coverage-item__row'>
            <span className='coverage-item__text-label me-1'>{gettext('source')}:</span>
            <span className='me-2'>{coverage.coverage_provider}</span>
        </div>
    );
}
