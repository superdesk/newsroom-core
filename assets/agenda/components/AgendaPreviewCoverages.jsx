import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {get, isEmpty} from 'lodash';

import {gettext, fullDate} from 'utils';
import {getCoveragesForDisplay, getCoverageIcon, getAgendaNames} from '../utils';

import PreviewBox from 'ui/components/PreviewBox';
import AgendaCoverages from './AgendaCoverages';
import AgendaInternalNote from './AgendaInternalNote';
import AgendaEdNote from './AgendaEdNote';

class AgendaPreviewCoverages extends React.Component {
    constructor(props) {
        super(props);

        this.state = {expanded: true};
        this.toggleExpanded = this.toggleExpanded.bind(this);
    }

    toggleExpanded() {
        this.setState((prevState) => ({expanded: !prevState.expanded}));
    }

    render() {
        const {item, wireItems, actions, user, plan, previewGroup, restrictCoverageInfo} = this.props;

        const displayCoverages = getCoveragesForDisplay(item, plan, previewGroup);

        if (isEmpty(displayCoverages.current) && isEmpty(displayCoverages.previous)) {
            return null;
        }

        const agendaNames = getAgendaNames(plan);

        return (item.item_type === 'planning' || restrictCoverageInfo) ? (
            <React.Fragment>
                {get(displayCoverages.current, 'length', 0) > 0 && (
                    <PreviewBox label={gettext('Coverages:')}>
                        <AgendaCoverages
                            item={item}
                            coverages={displayCoverages.current}
                            wireItems={wireItems}
                            actions={actions}
                            user={user}
                        />
                    </PreviewBox>
                )}

                {get(displayCoverages.previous, 'length', 0) > 0 && (
                    <PreviewBox label={gettext('Previous Coverages:')}>
                        <AgendaCoverages
                            item={item}
                            coverages={displayCoverages.previous}
                            wireItems={wireItems}
                            actions={actions}
                            user={user}
                        />
                    </PreviewBox>
                )}
            </React.Fragment>
        ) : (
            <div className={classNames(
                'agenda-planning__preview',
                {'agenda-planning__preview--expanded': this.state.expanded}
            )}>
                <div className="agenda-planning__preview-header">
                    <a href='#' onClick={this.toggleExpanded}>
                        <i className={classNames('icon-small--arrow-down me-1', {
                            'rotate-90-ccw': !this.state.expanded,
                        })} />
                    </a>
                    <h3 onClick={this.toggleExpanded}>{plan.name}</h3>
                </div>
                <p className="agenda-planning__preview-date">
                    {fullDate(plan.planning_date)}
                </p>
                {!this.state.expanded ? (
                    <div style={{display: 'flex', flexDirection: 'row', flexWrap: 'wrap'}}>
                        {displayCoverages.current.concat(displayCoverages.previous).map((coverage) => (
                            <i
                                key={coverage.coverage_id}
                                className={`icon-small--coverage-${getCoverageIcon(coverage.coverage_type)} me-2`}
                            />
                        ))}
                    </div>
                ) : (
                    <React.Fragment>
                        <div className="agenda-planning__preview-metadata">
                            {!agendaNames ? null : (
                                <div className="agenda-planning__preview-agendas">
                                    <i className="icon-small--calendar icon--gray-dark" />
                                    <span>{agendaNames}</span>
                                </div>
                            )}
                            <p>
                                {plan.description_text}
                            </p>

                            {!plan.ednote ? null : (
                                <AgendaEdNote
                                    item={plan}
                                    noMargin={true}
                                />
                            )}
                            {!plan.internal_note ? null : (
                                <AgendaInternalNote
                                    internalNote={plan.internal_note}
                                    noMargin={true}
                                />
                            )}
                        </div>

                        {get(displayCoverages.current, 'length', 0) > 0 && (
                            <PreviewBox label={gettext('Coverages:')}>
                                <AgendaCoverages
                                    item={item}
                                    coverages={displayCoverages.current}
                                    wireItems={wireItems}
                                    actions={actions}
                                    user={user}
                                />
                            </PreviewBox>
                        )}

                        {get(displayCoverages.previous, 'length', 0) > 0 && (
                            <PreviewBox label={gettext('Previous Coverages:')}>
                                <AgendaCoverages
                                    item={item}
                                    coverages={displayCoverages.previous}
                                    wireItems={wireItems}
                                    actions={actions}
                                    user={user}
                                />
                            </PreviewBox>
                        )}
                    </React.Fragment>
                )}
            </div>
        );
    }
}

export default AgendaPreviewCoverages;

AgendaPreviewCoverages.propTypes = {
    item: PropTypes.object,
    plan: PropTypes.object,
    previewGroup: PropTypes.string,
    wireItems: PropTypes.array,
    actions: PropTypes.array,
    user: PropTypes.string,
    restrictCoverageInfo: PropTypes.bool,
};
