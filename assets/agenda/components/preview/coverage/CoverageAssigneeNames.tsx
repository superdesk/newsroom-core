import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';
import {getCoverageAsigneeName, getCoverageDeskName} from 'agenda/utils';
import {gettext} from 'utils';

export function CoverageAssigneeNames({coverage, agenda}: ICoverageMetadataPreviewProps) {
    const assigneeName = getCoverageAsigneeName(coverage);
    const deskName = getCoverageDeskName(coverage);

    if (!assigneeName && !deskName) {
        return null;
    }

    const assignedUserEmail = coverage.assigned_user_email;
    const assignedDeskEmail = coverage.assigned_desk_email;
    const subject = gettext('Coverage inquiry from {{sitename}} user: {{item}}',
        {sitename: window.sitename, item: agenda.name || agenda.slugline || agenda.headline || ''});

    return (
        <div className="coverage-item__row align-items-center">
            {assigneeName && (
                <span className="d-flex text-nowrap pe-1">
                    <span className="coverage-item__text-label me-1">{gettext('assignee')}:</span>
                    {assignedUserEmail ? (
                        <a
                            href={`mailto:${assignedUserEmail}?subject=${subject}`}
                            target="_blank"
                        >
                            {assigneeName}
                        </a>
                    ) : (
                        <span>{assigneeName}</span>
                    )}
                </span>
            )}
            {assigneeName && deskName && ' | '}
            {deskName && (
                <span className="d-flex text-nowrap ps-1">
                    <span className="coverage-item__text-label me-1">{gettext('desk')}:</span>
                    {assignedDeskEmail ? (
                        <a
                            href={`mailto:${assignedDeskEmail}?subject=${subject}`}
                            target="_blank"
                        >
                            {deskName}
                        </a>
                    ) : (
                        <span>{deskName}</span>
                    )}
                </span>
            )}
        </div>
    );
}
