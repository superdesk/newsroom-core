import * as React from 'react';
import moment from 'moment-timezone';

import {ICoverageMetadataPreviewProps} from 'interfaces';
import {gettext, COVERAGE_DATE_TIME_FORMAT} from 'utils';
import {getNextPendingScheduledUpdate, WORKFLOW_STATUS} from 'agenda/utils';

export function CoverageScheduledStatus({coverage, fullCoverage}: ICoverageMetadataPreviewProps) {
    if (coverage.workflow_status !== WORKFLOW_STATUS.COMPLETED) {
        return null;
    }

    const scheduledUpdate = getNextPendingScheduledUpdate(fullCoverage);

    if (scheduledUpdate == null) {
        return null;
    }

    const dateString = moment(scheduledUpdate.planning.scheduled).format(COVERAGE_DATE_TIME_FORMAT);

    return (
        <div className='coverage-item__row'>
            <span>
                {gettext('Updated expected @ {{dateString}}', {dateString: dateString})}
            </span>
        </div>
    );
}
