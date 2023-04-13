import React from 'react';
import {connect} from 'react-redux';
import classNames from 'classnames';
import {isEmpty} from 'lodash';
import CoverageItemStatus from './CoverageItemStatus';
import {
    getDataFromCoverages,
    getCoverageDisplayName,
    getCoverageIcon,
    getCoverageTooltip,
    WORKFLOW_COLORS,
    WORKFLOW_STATUS,
    formatCoverageDate
} from '../utils';
import {agendaContentLinkTarget} from 'assets/ui/selectors';
import {gettext} from 'assets/utils';

interface IProps {
    item: any;
    coverages?: Array<any>;
    wireItems?: Array<any>;
    actions?: Array<any>;
    user?: string;
    onClick?: any;
    hideViewContentItems?: boolean;
    contentLinkTarget?: string;
}

function AgendaCoveragesComponent({
    item,
    coverages,
    wireItems,
    actions,
    user,
    onClick,
    hideViewContentItems,
    contentLinkTarget,
}: IProps) {
    if (isEmpty(coverages)) {
        return null;
    }

    const getSlugline = (coverage: any) => {
        const slugline = coverage.item_slugline || coverage.slugline;

        return slugline ? ` | ${slugline}` : '';
    };

    const coveragesWithoutState = coverages?.filter((coverage) => WORKFLOW_COLORS[coverage.workflow_status] == null);
    const coveragesWithState = coverages?.filter((coverage) => WORKFLOW_COLORS[coverage.workflow_status] != null);

    return (
        <React.Fragment>
            {!coveragesWithoutState?.length ? null : (
                <div>
                    {coveragesWithoutState.map((coverage) => (
                        <i
                            className={`icon--coverage-${getCoverageIcon(coverage.coverage_type)} me-2`}
                            key={coverage.coverage_id}
                            title={getCoverageTooltip(coverage)}
                        />
                    ))}
                </div>
            )}
            {coveragesWithState?.map((coverage) => (
                <div
                    className={classNames(
                        'coverage-item',
                        {'coverage-item--clickable': onClick}
                    )}
                    key={coverage.coverage_id}
                    onClick={onClick}
                    title={onClick ? gettext('Open Agenda in new tab') : onClick}
                >
                    <div
                        className='coverage-item__row flex-column align-items-start'
                        title={getCoverageTooltip(coverage)}
                    >
                        <span className={classNames('coverage-item__coverage-icon', WORKFLOW_COLORS[coverage.workflow_status])}>
                            <i className={`icon-small--coverage-${getCoverageIcon(coverage.coverage_type)} me-2`}></i>
                            <span>{`${getCoverageDisplayName(coverage.coverage_type)}${getSlugline(coverage)}`}</span>
                        </span>
                        {coverage.workflow_status !== WORKFLOW_STATUS.COMPLETED && coverage.scheduled != null && (
                            <span className='d-flex text-nowrap'>
                                <i className='icon-small--clock icon--gray-dark me-1'></i>
                                <span className='coverage-item__text-label me-1'>{gettext('expected')}:</span>
                                <span>{formatCoverageDate(coverage)}</span>
                            </span>
                        )}
                    </div>
                    {coverage.coverage_provider && (
                        <div className='coverage-item__row'>
                            <span className='coverage-item__text-label me-1'>{gettext('Source')}:</span>
                            <span className='me-2'>{coverage.coverage_provider}</span>
                        </div>
                    )}
                    <CoverageItemStatus
                        coverage={coverage}
                        item={item}
                        wireItems={wireItems}
                        actions={actions}
                        user={user}
                        coverageData={getDataFromCoverages(item)}
                        hideViewContentItems={hideViewContentItems}
                        contentLinkTarget={contentLinkTarget}
                    />
                </div>
            ))}
        </React.Fragment>
    );
}

const mapStateToProps = (state: any) => ({contentLinkTarget: agendaContentLinkTarget(state)});

const AgendaCoverages: React.ComponentType<IProps> = connect(mapStateToProps)(AgendaCoveragesComponent as any) as any;

export default AgendaCoverages;
