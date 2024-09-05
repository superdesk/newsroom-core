import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';
import {gettext} from 'utils';
import {isCoverageBeingUpdated} from 'agenda/utils';

export function CoverageUpdateComing({coverage}: ICoverageMetadataPreviewProps) {
    return !isCoverageBeingUpdated(coverage) ? null : (
        <div className='coverage-item__row'>
            <span className='label label--blue'>{gettext('Update coming')}</span>
        </div>
    );
}
