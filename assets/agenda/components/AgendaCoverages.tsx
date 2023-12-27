import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {isEmpty} from 'lodash';
import {gettext} from 'utils';
import CoverageItemStatus from './CoverageItemStatus';
import {
    getDataFromCoverages,
    getCoverageDisplayName,
    getCoverageIcon,
    getCoverageTooltip,
    WORKFLOW_COLORS,
    WORKFLOW_STATUS,
    formatCoverageDate,
    getCoverageAsigneeName,
    getCoverageDeskName
} from '../utils';
import {agendaContentLinkTarget} from 'ui/selectors';


function AgendaCoveragesComponent({item, coverages, wireItems, actions, user, onClick, hideViewContentItems, contentLinkTarget}: any) {
    if (isEmpty(coverages)) {
        return null;
    }

    const getSlugline = (coverage: any) => {
        const slugline = coverage.item_slugline || coverage.slugline;

        return slugline ? ` | ${slugline}` : '';
    };

    const coveragesWithoutState = coverages.filter((coverage: any) => WORKFLOW_COLORS[coverage.workflow_status] == null);
    const coveragesWithState = coverages.filter((coverage: any) => WORKFLOW_COLORS[coverage.workflow_status] != null);

    return (
        <React.Fragment>
            {!coveragesWithoutState.length ? null : (
                <div>
                    {coveragesWithoutState.map((coverage: any) => ( 
                        <i
                            className={`icon--coverage-${getCoverageIcon(coverage.coverage_type)} me-2`}
                            key={coverage.coverage_id}
                            title={getCoverageTooltip(coverage)}
                        />
                    ))}
                </div>
            )}
            {coveragesWithState.map((coverage: any) => {
                const assigneeName = getCoverageAsigneeName(coverage);
                const deskName = getCoverageDeskName(coverage);
                return(
                    <div
                        className={classNames(
                            'coverage-item',
                            {'coverage-item--clickable': onClick}
                        )}
                        key={coverage.coverage_id}
                        onClick={onClick}
                        title={onClick ? gettext('Open {{agenda}} in a new tab', window.sectionNames) : onClick}
                    >
                        <div
                            className='coverage-item__row coverage-item__row--header-row'
                            title={getCoverageTooltip(coverage)}
                        >
                            <span className={classNames('coverage-item__coverage-icon', WORKFLOW_COLORS[coverage.workflow_status])}>
                                <i className={`icon--coverage-${getCoverageIcon(coverage.coverage_type)}`}></i>
                            </span>

                            <span className='coverage-item__coverage-heading'>
                                <span className='fw-medium'>
                                    {`${(coverage.genre?.length ?? 0) > 0 ? gettext(coverage.genre[0].name) : getCoverageDisplayName(coverage.coverage_type)}`}
                                </span>
                                {`${getSlugline(coverage)}`}
                            </span>

                        </div>
                        {(assigneeName || deskName) && (
                            <div className='coverage-item__row align-items-center'>
                                {assigneeName && (
                                    <span className='d-flex text-nowrap pe-1'>
                                        <span className='coverage-item__text-label me-1'>{gettext('assignee')}:</span>
                                        <span>{assigneeName}</span>
                                    </span>
                                )}
                                {assigneeName && deskName && ' | '}
                                {deskName && (
                                    <span className='d-flex text-nowrap ps-1'>
                                        <span className='coverage-item__text-label me-1'>{gettext('desk')}:</span>
                                        <span className=''>{deskName}</span>
                                    </span>
                                )}
                            </div>
                        )}
                        {coverage.workflow_status !== WORKFLOW_STATUS.COMPLETED && coverage.scheduled != null && (
                            <div
                                className='coverage-item__row align-items-center'
                            >
                                <span className='d-flex text-nowrap'>
                                    <span className='coverage-item__text-label me-1'>{gettext('expected')}:</span>
                                    <span className=''>{formatCoverageDate(coverage)}</span>
                                </span>
                            </div>
                        )}



                        {coverage.coverage_provider && (
                            <div className='coverage-item__row'>
                                <span className='coverage-item__text-label me-1'>{gettext('source')}:</span>
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
                );})}
        </React.Fragment>
    );
}

AgendaCoveragesComponent.propTypes = {
    item: PropTypes.object,
    coverages: PropTypes.arrayOf(PropTypes.object),
    wireItems: PropTypes.array,
    actions: PropTypes.array,
    user: PropTypes.string,
    onClick: PropTypes.func,
    hideViewContentItems: PropTypes.bool,
    contentLinkTarget: PropTypes.string,
};

const mapStateToProps = (state: any) => ({
    contentLinkTarget: agendaContentLinkTarget(state),
});

const AgendaCoverages: React.ComponentType<any> = connect(mapStateToProps)(AgendaCoveragesComponent);

export default AgendaCoverages;
