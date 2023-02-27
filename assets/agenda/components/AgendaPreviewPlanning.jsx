import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';
import {isPlanningItem} from '../utils';
import AgendaPreviewCoverages from './AgendaPreviewCoverages';

export class AgendaPreviewPlanning extends React.Component {
    render() {
        const {
            item,
            planningId,
            wireItems,
            coverageActions,
            user,
            previewGroup,
            restrictCoverageInfo,
        } = this.props;

        const planningItems = get(item, 'planning_items') || [];
        const plan = planningItems.find((p) => p.guid === planningId);
        const otherPlanningItems = planningItems.filter((p) => p.guid !== planningId);

        if (isPlanningItem(item) || restrictCoverageInfo) {
            return (
                <AgendaPreviewCoverages
                    key={item.guid}
                    item={item}
                    plan={plan}
                    wireItems={wireItems}
                    actions={coverageActions}
                    user={user}
                    previewGroup={previewGroup}
                    restrictCoverageInfo={restrictCoverageInfo}
                />
            );
        }

        return (
            <React.Fragment>
                {!plan ? null : (
                    <div className="agenda-planning__container info-box">
                        <div className="info-box__content">
                            <span className="info-box__label">
                                {gettext('Planning Item')}
                            </span>
                            <AgendaPreviewCoverages
                                key={plan.guid}
                                item={item}
                                plan={plan}
                                wireItems={wireItems}
                                actions={coverageActions}
                                user={user}
                                previewGroup={previewGroup}
                            />
                        </div>
                    </div>
                )}
                {!otherPlanningItems.length ? null : (
                    <div className="agenda-planning__container info-box">
                        <div className="info-box__content">
                            <span className="info-box__label">
                                {gettext('Other Planning Items')}
                            </span>
                            {otherPlanningItems.map((planningItem) => (
                                <AgendaPreviewCoverages
                                    key={planningItem.guid}
                                    item={item}
                                    plan={planningItem}
                                    wireItems={wireItems}
                                    actions={coverageActions}
                                    user={user}
                                    previewGroup={previewGroup}
                                />
                            ))}
                        </div>
                    </div>
                )}
            </React.Fragment>
        );
    }
}

AgendaPreviewPlanning.propTypes = {
    user: PropTypes.string,
    item: PropTypes.object,
    planningId: PropTypes.string,
    wireItems: PropTypes.array,
    coverageActions: PropTypes.array,
    previewGroup: PropTypes.string,
    restrictCoverageInfo: PropTypes.bool,
};
