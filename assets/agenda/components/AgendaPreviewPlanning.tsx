import * as React from 'react';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {isPlanningItem} from '../utils';
import {fetchItemsByIdToRedux} from '../actions';
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
    planningItems?: Array<IAgendaItem>;
    fetchItemsByIdToRedux: (ids: string[]) => Promise<void>;
}

interface IReduxStateProps {
    wireItems?: Array<IArticle>;
    items: Array<IAgendaItem>;
}

interface IState {
    loading: boolean;
    expandedPlanningItems: Record<string, boolean>;
}

type IProps = IOwnProps & IReduxStateProps;

class AgendaPreviewPlanningComponent extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {
            loading: false,
            expandedPlanningItems: {},
        };

        this.fetchSecondaryPlanningItems = this.fetchSecondaryPlanningItems.bind(this);
        this.toggleExpanded = this.toggleExpanded.bind(this);
    }

    componentDidMount() {
        this.fetchSecondaryPlanningItems();
    }

    componentDidUpdate(prevProps: IProps) {
        if (prevProps.item !== this.props.item) {
            this.fetchSecondaryPlanningItems();
        }
    }

    fetchSecondaryPlanningItems() {
        const {item, planningId, fetchItemsByIdToRedux} = this.props;
        const planningIds = item.planning_ids?.filter((id:string) => id !== planningId) || [];

        this.setState({loading: true});

        if (planningIds == null || planningIds.length == 0) {
            return;
        }
        
        this.setState({loading: true});
        
        fetchItemsByIdToRedux(planningIds)
            .finally(() => {
                this.setState({loading: false});
            })
            .catch((error) => {
                console.error('Error fetching items:', error);
                this.setState({loading: false});
            });
    }

    toggleExpanded(planningItemId: string) {
        this.setState((prevState) => ({
            expandedPlanningItems: {
                ...prevState.expandedPlanningItems,
                [planningItemId]: !prevState.expandedPlanningItems[planningItemId],
            },
        }));
    }

    getRelatedPlanningItems() {
        const {item, items} = this.props;
        return (item.planning_ids || []).map((id:any) => items[id]);
    }

    render() {
        const {
            item,
            planningId,
            wireItems,
            coverageActions,
            user,
            previewGroup,
            restrictCoverageInfo,
            previewConfig,
        } = this.props;
        const {loading, expandedPlanningItems} = this.state;

        const planningItems = item.planning_items || [];
        const plan = planningItems.find((p) => p.guid === planningId);
        const otherPlanningItems = planningItems.filter((p) => p.guid !== planningId);
        const relatedPlanningItems = this.getRelatedPlanningItems();

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
                {/* Current Planning Items */}
                {!plan ? null : (
                    <div className="agenda-planning__container info-box">
                        <div className="info-box__content">
                            <span className="info-box__label">{gettext('Planning Item')}</span>
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
                    <div className="agenda-planning__container info-box">
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
                {/* Related Planning Items */}
                <div className="agenda-planning__container info-box">
                    <div className="info-box__content">
                        <span className="info-box__label">
                            {gettext('Related Planning Items')}
                        </span>
                        {loading ? (
                            <div className="spinner-border text-success" />
                        ) : (
                            relatedPlanningItems && relatedPlanningItems.map((planningItem: any) => {
                                const isExpanded = expandedPlanningItems[planningItem._id] || false;
                                return (
                                    <div
                                        key={planningItem.guid}
                                        className={`agenda-planning__preview ${
                                            isExpanded
                                                ? 'agenda-planning__preview--expanded'
                                                : ''
                                        }`}
                                    >
                                        <div
                                            className="agenda-planning__preview-header"
                                            onClick={() =>
                                                this.toggleExpanded(planningItem._id)
                                            }
                                        >
                                            <i
                                                className={`icon-small--arrow-down ${
                                                    isExpanded ? '' : 'rotate-90-ccw'
                                                }`}
                                            />
                                            <span>{planningItem.headline || 'No Headline'}</span>
                                        </div>
                                        {isExpanded && (
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
                                        )}
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>
            </React.Fragment>
        );
    }
}

const mapStateToProps = (state: any, ownProps: any) => {
    return {
        items: state.itemsById,
        wireItems: state.agenda.agendaWireItems || [],
    };
};

const mapDispatchToProps = (dispatch: any) => ({
    fetchItemsByIdToRedux: (ids: string[]) => dispatch(fetchItemsByIdToRedux(ids)),
});

export const AgendaPreviewPlanning = connect(mapStateToProps, mapDispatchToProps)(AgendaPreviewPlanningComponent);
