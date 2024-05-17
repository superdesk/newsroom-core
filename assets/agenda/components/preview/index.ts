import * as React from 'react';

import {ICoverageMetadataPreviewProps} from 'interfaces';

// Core fields
import {CoverageMetadataPreviewHeader} from './coverage/CoverageMetadataPreviewHeader';
import {CoverageAssigneeNames} from './coverage/CoverageAssigneeNames';
import {CoverageExpectedDate} from './coverage/CoverageExpectedDate';
import {CoverageProvider} from './coverage/CoverageProvider';
import {CoverageWireText} from './coverage/CoverageWireText';
import {CoverageUpdateComing} from './coverage/CoverageUpdateComing';
import {CoverageStatus} from './coverage/CoverageStatus';
import {CoverageEdnote} from './coverage/CoverageEdnote';
import {CoverageScheduledStatus} from './coverage/CoverageScheduledStatus';
import {CoverageWorkflowReason} from './coverage/CoverageWorkflowReason';
import {CoverageInternalNote} from './coverage/CoverageInternalNote';
import {CoverageActions} from './coverage/CoverageActions';

export const DEFAULT_COVERAGE_METADATA_FIELDS = [
    'coverage_header',
    'coverage_assignee_names',
    'coverage_expected_date',
    'coverage_provider',
    'coverage_wire_text',
    'coverage_update_coming',
    'coverage_status',
    'coverage_scheduled_status',
    'coverage_ednote',
    'coverage_workflow_reason',
    'coverage_internal_note',
    'coverage_actions',
];

export const coverageFieldToComponentMap: {[key: string]: React.ComponentType<ICoverageMetadataPreviewProps>} = {
    coverage_header: CoverageMetadataPreviewHeader,
    coverage_assignee_names: CoverageAssigneeNames,
    coverage_expected_date: CoverageExpectedDate,
    coverage_provider: CoverageProvider,
    coverage_wire_text: CoverageWireText,
    coverage_update_coming: CoverageUpdateComing,
    coverage_status: CoverageStatus,
    coverage_scheduled_status: CoverageScheduledStatus,
    coverage_ednote: CoverageEdnote,
    coverage_workflow_reason: CoverageWorkflowReason,
    coverage_internal_note: CoverageInternalNote,
    coverage_actions: CoverageActions,
};

export function registerCoverageFieldComponent(field: string, component: React.ComponentType<ICoverageMetadataPreviewProps>) {
    coverageFieldToComponentMap[field] = component;
}
