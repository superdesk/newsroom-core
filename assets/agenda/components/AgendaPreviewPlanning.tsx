import * as React from 'react';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {isPlanningItem} from '../utils';
import AgendaPreviewCoverages from './AgendaPreviewCoverages';
import {IAgendaItem, ICoverageItemAction, IUser, IAgendaPreviewConfig, IArticle, IAgendaState} from 'interfaces';

interface IOwnProps {
    item: IAgendaItem;
    planningId?: IAgendaItem['_id'];
    user?: IUser['_id'];
    coverageActions?: Array<ICoverageItemAction>;
    previewGroup?: string;
    restrictCoverageInfo?: boolean;
    previewConfig: IAgendaPreviewConfig;
}

interface IReduxStateProps {
    wireItems?: Array<IArticle>;
}

type IProps = IOwnProps & IReduxStateProps;

function AgendaPreviewPlanningComponent({
    item,
    planningId,
    wireItems,
    coverageActions,
    user,
    previewGroup,
    restrictCoverageInfo,
    previewConfig,
}: IProps) {
    const planningItems = item.planning_items || [];
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
                previewConfig={previewConfig}
            />
        );
    }

    return (
        <React.Fragment>
            {!plan ? null : (
                <div className="agenda-planning__container">
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
                            previewConfig={previewConfig}
                        />
                    </div>
                </div>
            )}
            {!otherPlanningItems.length ? null : (
                <div className="agenda-planning__container">
                    <div className="info-box__content">
                        <span className="info-box__label">
                            {plan == null ? gettext('Planning Items') : gettext('Other Planning Items')}
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
                                previewConfig={previewConfig}
                            />
                        ))}
                    </div>
                </div>
            )}
        </React.Fragment>
    );
}

const mapStateToProps = (state: IAgendaState): IReduxStateProps => ({
    wireItems: state.agenda.agendaWireItems || [],
});

export const AgendaPreviewPlanning = connect<
    IReduxStateProps,
    {},
    IOwnProps,
    IAgendaState
>(mapStateToProps)(AgendaPreviewPlanningComponent);
