import * as React from 'react';
import classNames from 'classnames';

import {ICoverageMetadataPreviewProps} from 'interfaces';

import {gettext} from 'utils';
import {
    getCoverageDisplayName,
    getCoverageIcon,
    getCoverageTooltip,
    isCoverageBeingUpdated,
    WORKFLOW_COLORS,
} from 'agenda/utils';

export function CoverageMetadataPreviewHeader({coverage}: ICoverageMetadataPreviewProps) {
    const slugline = coverage.slugline || '';

    return (
        <div
            className='coverage-item__row coverage-item__row--header-row'
            title={getCoverageTooltip(coverage, isCoverageBeingUpdated(coverage))}
        >
            <span
                className={classNames('coverage-item__coverage-icon', WORKFLOW_COLORS[coverage.workflow_status])}>
                <i className={`icon--coverage-${getCoverageIcon(coverage.coverage_type)}`}></i>
            </span>
            <span className='coverage-item__coverage-heading'>
                <span className='fw-medium'>
                    {`${coverage.genre && (coverage.genre?.length ?? 0) > 0 ? gettext(
                        coverage.genre[0].name) : getCoverageDisplayName(coverage.coverage_type)}`}
                </span>
                {slugline.length === 0 ? null : ` | ${slugline}`}
            </span>
        </div>
    );
}
