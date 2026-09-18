import * as React from 'react';
import {connect} from 'react-redux';
import classNames from 'classnames';

import {gettext} from 'utils';
import {getName, getInternalNote, getFilteredItems} from '../utils';
import {fetchItemsByIdToRedux} from '../actions';

import AgendaTime from './AgendaTime';
import AgendaListItemLabels from './AgendaListItemLabels';
import AgendaMeta from './AgendaMeta';
import AgendaLongDescription from './AgendaLongDescription';
import AgendaPreviewAttachments from './AgendaPreviewAttachments';
import AgendaTags from './AgendaTags';
import AgendaEdNote from './AgendaEdNote';
import AgendaInternalNote from './AgendaInternalNote';
import {IAgendaItem} from 'interfaces';

interface AgendaPreviewEventProps {
    item: IAgendaItem;
    itemsById: Array<IAgendaItem>;
    eventIds: Array<string>;
    fetchItemsByIdToRedux: (ids: Array<string>) => Promise<void>;
}

interface AgendaPreviewEventState {
    loading: boolean;
    expandedEvents: Record<string, boolean>;
}

class AgendaPreviewEventComponent extends React.Component<AgendaPreviewEventProps, AgendaPreviewEventState> {
    constructor(props: AgendaPreviewEventProps) {
        super(props);

        this.state = {
            loading: true,
            expandedEvents: {},
        };

        this.toggleExpanded = this.toggleExpanded.bind(this);
        this.reloadEvent = this.reloadEvent.bind(this);
    }

    componentDidMount() {
        this.reloadEvent();
    }

    componentDidUpdate(prevProps: AgendaPreviewEventProps) {
        if (prevProps.eventIds !== this.props.eventIds) {
            this.reloadEvent();
        }
    }

    reloadEvent() {
        const {eventIds, fetchItemsByIdToRedux} = this.props;
    
        if (eventIds == null || eventIds.length == 0) {
            this.setState({loading: false});
            return;
        }
        
    
        this.setState({loading: true});
        
        fetchItemsByIdToRedux(eventIds)
            .finally(() => {
                this.setState({loading: false});
            })
            .catch((error) => {
                console.error('Error fetching items:', error);
                this.setState({loading: false});
            });
    }

    toggleExpanded(eventId: string) {
        this.setState((prevState) => ({
            expandedEvents: {
                ...prevState.expandedEvents,
                [eventId]: !prevState.expandedEvents[eventId],
            },
        }));
    }

    renderEvent(item: IAgendaItem) {
        const isExpanded = this.state.expandedEvents[item._id] || false;

        return (
            <div
                key={item._id}
                className={classNames('agenda-planning__preview', {
                    'agenda-planning__preview--expanded': isExpanded,
                })}
            >
                <div className="agenda-planning__preview-header">
                    <a href="#" onClick={() => this.toggleExpanded(item._id)}>
                        <i
                            className={classNames('icon-small--arrow-down me-1', {
                                'rotate-90-ccw': !isExpanded,
                            })}
                        />
                    </a>
                    <h3 onClick={() => this.toggleExpanded(item._id)}>{getName(item)}</h3>
                </div>
                <div className="agenda-planning__preview-date">
                    <AgendaTime item={item}>
                        <AgendaListItemLabels item={item} />
                    </AgendaTime>
                </div>
                {!isExpanded ? null : (
                    <div className="agenda-planning__preview-metadata">
                        <AgendaMeta item={item} />
                        <AgendaLongDescription item={item} />
                        <AgendaPreviewAttachments item={item} />
                        <AgendaTags item={item} isItemDetail={false} />
                        <AgendaEdNote
                            item={item}
                            plan={{}}
                            secondaryNoteField="state_reason"
                        />
                        <AgendaInternalNote
                            internalNote={getInternalNote(item, {})}
                            mt2={!!(item.ednote || item.state_reason)}
                        />
                    </div>
                )}
            </div>
        );
    }

    render() {
        const {itemsById, eventIds} = this.props;

        const filteredEvents = getFilteredItems(eventIds, itemsById);

        return (
            <div className="agenda-planning__container">
                <div className="preview__content-block">
                    <div className="preview__content-block-title">
                        {gettext('Related Events')}
                    </div>
                    <div className="agenda-planning__preview-list">
                        {this.state.loading ? (
                            <div className="spinner-border text-success" />
                        ) : filteredEvents.length === 0 ? (
                            <div>{gettext('No Related Events')}</div>
                        ) : (
                            filteredEvents.map((event) => this.renderEvent(event))
                        )}
                    </div>
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state: any, ownProps: any) => ({
    itemsById: state.itemsById,
    eventIds: ownProps.item.event_ids || [],
});

const mapDispatchToProps = (dispatch: any) => ({
    fetchItemsByIdToRedux: (ids: Array<string>) => dispatch(fetchItemsByIdToRedux(ids)),
});

export const AgendaPreviewEvent = connect(mapStateToProps, mapDispatchToProps)(AgendaPreviewEventComponent);