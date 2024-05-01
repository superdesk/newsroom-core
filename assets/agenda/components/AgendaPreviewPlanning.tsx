import * as React from 'react';

import {gettext} from 'utils';
import {isPlanningItem} from '../utils';
import AgendaPreviewCoverages from './AgendaPreviewCoverages';
import {IAgendaItem, ICoverageItemAction, IUser, IAgendaPreviewConfig, IArticle} from 'interfaces';

interface IProps {
    item: IAgendaItem;
    planningId?: IAgendaItem['_id'];
    user?: IUser['_id'];
    wireItems?: Array<IArticle>;
    coverageActions?: Array<ICoverageItemAction>;
    previewGroup?: string;
    restrictCoverageInfo?: boolean;
    previewConfig: IAgendaPreviewConfig;
}

export class AgendaPreviewPlanning extends React.Component<IProps, any> {
    static propTypes: any;
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
                    previewConfig={this.props.previewConfig}
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
                                previewConfig={this.props.previewConfig}
                            />
                        </div>
                    </div>
                )}
                {!otherPlanningItems.length ? null : (
                    <div className="agenda-planning__container info-box">
                        <div className="info-box__content">
                            <span className="info-box__label">
                                {plan == null ? gettext('Planning Items') : gettext('Other Planning Items')}
                            </span>
                            {otherPlanningItems.map((planningItem: any) => (
                                <AgendaPreviewCoverages
                                    key={planningItem.guid}
                                    item={item}
                                    plan={planningItem}
                                    wireItems={wireItems}
                                    actions={coverageActions}
                                    user={user}
                                    previewGroup={previewGroup}
                                    previewConfig={this.props.previewConfig}
                                />
                            ))}
                        </div>
                    </div>
                )}
            </React.Fragment>
        );
    }
}
