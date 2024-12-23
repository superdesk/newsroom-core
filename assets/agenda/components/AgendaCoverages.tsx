import React from 'react';
import classNames from 'classnames';

import {
    IAgendaItem,
    IAgendaPreviewConfig,
    IArticle,
    ICoverage,
    ICoverageItemAction,
    IUser
} from 'interfaces';
import {gettext} from 'utils';
import {getCoverageIcon, getCoverageTooltip, WORKFLOW_COLORS} from '../utils';
import {coverageFieldToComponentMap, DEFAULT_COVERAGE_METADATA_FIELDS} from './preview';

interface IProps {
    item: IAgendaItem;
    coverages?: Array<ICoverage>;
    wireItems?: Array<IArticle>;
    actions?: Array<ICoverageItemAction>;
    user?: IUser['_id'];
    hideViewContentItems?: Array<IArticle['_id']>;
    previewConfig?: IAgendaPreviewConfig;
    onClick?(): void;
}

export default function AgendaCoverages({
    item,
    coverages,
    wireItems,
    actions,
    user,
    onClick,
    hideViewContentItems,
    previewConfig,
}: IProps) {
    if (coverages == null || coverages.length === 0) {
        return null;
    }

    const coveragesWithoutState = coverages.filter((coverage) => WORKFLOW_COLORS[coverage.workflow_status] == null);
    const coveragesWithState = coverages.filter((coverage) => WORKFLOW_COLORS[coverage.workflow_status] != null);
    const coverageFieldsToRender = previewConfig?.coverage_metadata_fields ?? DEFAULT_COVERAGE_METADATA_FIELDS;

    return (
        <React.Fragment>
            {!coveragesWithoutState.length ? null : (
                <div>
                    {coveragesWithoutState.map((coverage: ICoverage) => (
                        <i
                            className={`icon--coverage-${getCoverageIcon(coverage.coverage_type)} me-2`}
                            key={coverage.coverage_id}
                            title={getCoverageTooltip(coverage)}
                        />
                    ))}
                </div>
            )}
            <div className='coverage-item__list'>
                {coveragesWithState.map((coverage: ICoverage) => {
                    return (
                        <div
                            className={classNames(
                                'coverage-item',
                                {'coverage-item--clickable': onClick}
                            )}
                            key={coverage.coverage_id}
                            onClick={onClick}
                            title={onClick ? gettext('Open {{agenda}} in a new tab', window.sectionNames) : ''}
                        >
                            {coverageFieldsToRender.map((field) => {
                                const FieldComponent = coverageFieldToComponentMap[field];

                                if (FieldComponent == null) {
                                    console.warn(`Component not registered for field ${field}`);
                                    return null;
                                }

                                return (
                                    <FieldComponent
                                        key={field}
                                        agenda={item}
                                        coverage={coverage}
                                        wireItems={wireItems}
                                        actions={actions}
                                        user={user}
                                        hideViewContentItems={hideViewContentItems}
                                        fullCoverage={
                                            (item.planning_items || [])
                                                .find((planningItem) => planningItem._id === coverage.planning_id)
                                                ?.coverages?.find((coverageItem) => coverageItem.coverage_id === coverage.coverage_id)
                                        }
                                    />
                                );
                            })}
                        </div>
                    );})}
            </div>
        </React.Fragment>
    );
}
