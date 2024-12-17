import * as React from 'react';
import {connect} from 'react-redux';
import classNames from 'classnames';
import {get} from 'lodash';

import {gettext} from 'utils';
import {getName, getInternalNote} from '../utils';
import {fetchItem} from '../actions';

import AgendaTime from './AgendaTime';
import AgendaListItemLabels from './AgendaListItemLabels';
import AgendaMeta from './AgendaMeta';
import AgendaLongDescription from './AgendaLongDescription';
import AgendaPreviewAttachments from './AgendaPreviewAttachments';
import AgendaTags from './AgendaTags';
import AgendaEdNote from './AgendaEdNote';
import AgendaInternalNote from './AgendaInternalNote';

class AgendaPreviewEventComponent extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any) {
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

    componentDidUpdate(prevProps: any) {
        if (get(prevProps.item, 'event_ids') !== get(this.props.item, 'event_ids')) {
            this.reloadEvent();
        }
    }

    reloadEvent() {
        const {item, fetchEvent} = this.props;
        const eventIds = item.event_ids || [];

        this.setState({loading: true});
        Promise.all(eventIds.map((id: string) => fetchEvent(id)))
            .catch((error) => console.error('Failed to fetch events:', error))
            .finally(() => this.setState({loading: false}));
    }

    toggleExpanded(eventId: string) {
        this.setState((prevState: any) => ({
            expandedEvents: {
                ...prevState.expandedEvents,
                [eventId]: !prevState.expandedEvents[eventId],
            },
        }));
    }

    renderEvent(item: any) {
        const isExpanded = this.state.expandedEvents[item.guid] || false;
        return (
            <div
                key={item.id}
                className={classNames('agenda-planning__preview', {
                    'agenda-planning__preview--expanded': isExpanded,
                })}
            >
                <div className="agenda-planning__preview-header">
                    <a href="#" onClick={() => this.toggleExpanded(item.guid)}>
                        <i
                            className={classNames('icon-small--arrow-down me-1', {
                                'rotate-90-ccw': !isExpanded,
                            })}
                        />
                    </a>
                    <h3 onClick={() => this.toggleExpanded(item.guid)}>{getName(item)}</h3>
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
        return (
            <div className="agenda-planning__container info-box">
                <div className="info-box__content">
                    <span className="info-box__label">{gettext('Related Events')}</span>
                    {this.state.loading ? (
                        <div className="spinner-border text-success" />
                    ) : (
                        this.props.events.map((event: any) => this.renderEvent(event))
                    )}
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state: any, ownProps: any) => {
    const eventIds = ownProps.item.event_ids || [];
    return {
        events: eventIds.map((eventId: string) => state.itemsById[eventId]),
    };
};

const mapDispatchToProps = (dispatch: any) => ({
    fetchEvent: (eventId: string) => dispatch(fetchItem(eventId)),
});

export const AgendaPreviewEvent = connect(mapStateToProps, mapDispatchToProps)(AgendaPreviewEventComponent);
