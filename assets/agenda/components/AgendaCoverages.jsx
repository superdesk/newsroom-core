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
    formatCoverageDate
} from '../utils';
import {agendaContentLinkTarget} from 'ui/selectors';


function AgendaCoveragesComponent({item, coverages, wireItems, actions, user, onClick, hideViewContentItems, contentLinkTarget}) {
    if (isEmpty(coverages)) {
        return null;
    }

    const getSlugline = (coverage) => {
        const slugline = coverage.item_slugline || coverage.slugline;

        return slugline ? ` | ${slugline}` : '';
    };

    const coveragesWithoutState = coverages.filter((coverage) => WORKFLOW_COLORS[coverage.workflow_status] == null);
    const coveragesWithState = coverages.filter((coverage) => WORKFLOW_COLORS[coverage.workflow_status] != null);

    return (
        <React.Fragment>
            {!coveragesWithoutState.length ? null : (
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
            {coveragesWithState.map((coverage) => (
                <div
                    className={classNames(
                        'coverage-item',
                        {'coverage-item--clickable': onClick}
                    )}
                    key={coverage.coverage_id}
                    onClick={onClick}
                    title={onClick ? gettext('Open {{agenda}} in a new tab', sectionNames) : onClick}
                >
                    <div
                        className='coverage-item__row flex-column align-items-start'
                        title={getCoverageTooltip(coverage)}
                    >
                        <span className={classNames('coverage-item__coverage-icon', WORKFLOW_COLORS[coverage.workflow_status])}>
                            <i className={`icon-small--coverage-${getCoverageIcon(coverage.coverage_type)} me-2`}></i>
                            <span>{`${coverage.genre.length !==0 ? gettext(coverage.genre[0].name) : getCoverageDisplayName(coverage.coverage_type)}${getSlugline(coverage)}`}</span>
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

const mapStateToProps = (state) => ({
    contentLinkTarget: agendaContentLinkTarget(state),
});

const AgendaCoverages = connect(mapStateToProps)(AgendaCoveragesComponent);

export default AgendaCoverages;
