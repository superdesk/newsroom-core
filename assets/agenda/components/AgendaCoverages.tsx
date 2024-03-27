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
import {ICoverage} from 'interfaces';


function AgendaCoveragesComponent({item, coverages, wireItems, actions, user, onClick, hideViewContentItems, contentLinkTarget}: any) {
    if (isEmpty(coverages)) {
        return null;
    }

    const getSlugline = (coverage: any) => {
        const slugline = coverage.item_slugline || coverage.slugline;

        return slugline ? ` | ${slugline}` : '';
    };

    const coveragesWithoutState = coverages.filter((coverage: ICoverage) => WORKFLOW_COLORS[coverage.workflow_status] == null);
    const coveragesWithState = coverages.filter((coverage: ICoverage) => WORKFLOW_COLORS[coverage.workflow_status] != null);

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
            {coveragesWithState.map((coverage: ICoverage) => {
                const assigneeName = getCoverageAsigneeName(coverage);
                const deskName = getCoverageDeskName(coverage);
                const assignedUserEmail = coverage.assigned_user_email;
                const assignedDeskEmail = coverage.assigned_desk_email;
                const subject = gettext('Coverage inquiry from {{sitename}} user: {{item}}',
                    {sitename: window.sitename, item: item.name || item.slugline});
                return(
                    <div
                        className={classNames(
                            'coverage-item',
                            {'coverage-item--clickable': onClick}
                        )}
                        key={coverage.coverage_id}
                        onClick={onClick}
                        title={onClick ? gettext('Open {{agenda}} in a new tab', window.sectionNames) : ''}
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
                                    {`${coverage.genre && (coverage.genre?.length ?? 0) > 0 ? gettext(
                                        coverage.genre[0].name) : getCoverageDisplayName(coverage.coverage_type)}`}
                                </span>
                                {getSlugline(coverage)}
                            </span>

                        </div>
                        {(assigneeName || deskName) && (
                            <div className='coverage-item__row align-items-center'>
                                {assigneeName && (
                                    <span className='d-flex text-nowrap pe-1'>
                                        <span className='coverage-item__text-label me-1'>{gettext('assignee')}:</span>
                                        {assignedUserEmail ? <a href={`mailto:${assignedUserEmail}?subject=${subject}`} 
                                            target="_blank">{assigneeName}</a> : <span>{assigneeName}</span> }
                                    </span>
                                )}
                                {assigneeName && deskName && ' | '}
                                {deskName && (
                                    <span className='d-flex text-nowrap ps-1'>
                                        <span className='coverage-item__text-label me-1'>{gettext('desk')}:</span>
                                        {assignedDeskEmail ? <a href={`mailto:${assignedDeskEmail}?subject=${subject}`}
                                            target="_blank">{deskName}</a> : <span>{deskName}</span>}
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
