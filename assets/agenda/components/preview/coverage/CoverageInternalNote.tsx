import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';

import AgendaInternalNote from 'agenda/components/AgendaInternalNote';

export function CoverageInternalNote({fullCoverage}: ICoverageMetadataPreviewProps) {
    return fullCoverage == null || (fullCoverage.internal_note ?? '').length === 0 ? null : (
        <div className='coverage-item__row'>
            <AgendaInternalNote internalNote={fullCoverage.internal_note} noMargin/>
        </div>
    );
}
