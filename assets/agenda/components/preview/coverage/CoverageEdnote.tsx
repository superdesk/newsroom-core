import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';
import AgendaEdNote from 'agenda/components/AgendaEdNote';

export function CoverageEdnote({coverage, wireItems, fullCoverage}: ICoverageMetadataPreviewProps) {
    const wireItem = coverage.delivery_id == null ? null : (wireItems || []).find(
        (content) => content._id === coverage.delivery_id
    );
    const edNote = wireItem?.ednote ?? fullCoverage?.planning?.ednote ?? '';

    return edNote.length === 0 ? null : (
        <div className='coverage-item__row'>
            <AgendaEdNote item={{ednote: edNote}} noMargin/>
        </div>
    );
}
