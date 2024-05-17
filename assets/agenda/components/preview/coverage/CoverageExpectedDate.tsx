import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';
import {formatCoverageDate, WORKFLOW_STATUS} from 'agenda/utils';
import {gettext} from 'utils';

export function CoverageExpectedDate({coverage}: ICoverageMetadataPreviewProps) {
    if (coverage.workflow_status === WORKFLOW_STATUS.COMPLETED || coverage.scheduled == null) {
        return null;
    }

    return (
        <div
            className='coverage-item__row align-items-center'
        >
            <span className='d-flex text-nowrap'>
                <span className='coverage-item__text-label me-1'>{gettext('expected')}:</span>
                <span className=''>{formatCoverageDate(coverage)}</span>
            </span>
        </div>
    );
}
