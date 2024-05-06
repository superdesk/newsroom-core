import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';
import {gettext} from 'utils';
import AgendaEdNote from 'agenda/components/AgendaEdNote';

export function CoverageWorkflowReason({fullCoverage}: ICoverageMetadataPreviewProps) {
    let reason = fullCoverage?.workflow_status_reason ?? '';

    if (reason.length === 0) {
        return null;
    }

    const COVERAGE_CANCELLED_PREFIX = 'All coverages cancelled: ';
    const PLANNING_CANCELLED_PREFIX = 'Planning cancelled: ';

    if (reason.startsWith(COVERAGE_CANCELLED_PREFIX)) {
        reason = reason.substring(COVERAGE_CANCELLED_PREFIX.length);
        reason = gettext('All coverages cancelled: {{ reason }}', {reason: reason});
    } else if (reason.startsWith(PLANNING_CANCELLED_PREFIX)) {
        reason = reason.substring(PLANNING_CANCELLED_PREFIX.length);
        reason = gettext('Planning cancelled: {{ reason }}', {reason: reason});
    }

    return (
        <div className='coverage-item__row'>
            <AgendaEdNote item={{ednote: reason}} noMargin/>
        </div>
    );
}
