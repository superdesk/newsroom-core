import * as React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';
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

class AgendaPreviewEventComponent extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            loading: true,
            expanded: false,
        };
        this.toggleExpanded = this.toggleExpanded.bind(this);
    }

    componentDidMount() {
        this.reloadEvent();
    }

    componentDidUpdate(prevProps) {
        if (get(prevProps.item, 'event_id') !== get(this.props.item, 'event_id')) {
            this.reloadEvent();
        }
    }

    reloadEvent() {
        this.setState({loading: true}, () => {
            this.props
                .fetchEvent(this.props.item.event_id)
                .finally(() => {
                    this.setState({loading: false});
                });
        });
    }

    toggleExpanded() {
        this.setState((prevState) => ({expanded: !prevState.expanded}));
    }

    render() {
        if (!this.state.loading && this.props.event == null) {
            // If we're not loading and there is no event,
            // then an error has occurred (user already notified via props.fetchEvent)
            return null;
        }

        return (
            <div className="agenda-planning__container info-box">
                <div className="info-box__content">
                    <span className="info-box__label">
                        {gettext('Associated Event')}
                    </span>
                    <div className={classNames(
                        'agenda-planning__preview',
                        {'agenda-planning__preview--expanded': this.state.expanded}
                    )}>
                        {this.state.loading ? (
                            <div className="spinner-border text-success" />
                        ) : (
                            <React.Fragment>
                                <div className="agenda-planning__preview-header">
                                    <a href='#' onClick={this.toggleExpanded}>
                                        <i className={classNames('icon-small--arrow-down me-1', {
                                            'rotate-90-ccw': !this.state.expanded,
                                        })} />
                                    </a>
                                    <h3 onClick={this.toggleExpanded}>{getName(this.props.event)}</h3>
                                </div>
                                <div className="agenda-planning__preview-date">
                                    <AgendaTime item={this.props.event}>
                                        <AgendaListItemLabels item={this.props.event} />
                                    </AgendaTime>
                                </div>
                                {!this.state.expanded ? null : (
                                    <div className="agenda-planning__preview-metadata">
                                        <AgendaMeta item={this.props.event} />
                                        <AgendaLongDescription item={this.props.event} />
                                        <AgendaPreviewAttachments item={this.props.event} />
                                        <AgendaTags
                                            item={this.props.event}
                                            isItemDetail={false}
                                        />
                                        <AgendaEdNote
                                            item={this.props.event}
                                            plan={{}}
                                            secondaryNoteField="state_reason"
                                        />
                                        <AgendaInternalNote
                                            internalNote={getInternalNote(this.props.event, {})}
                                            mt2={!!(this.props.event.ednote || this.props.event.state_reason)}
                                        />
                                    </div>
                                )}
                            </React.Fragment>
                        )}
                    </div>
                </div>
            </div>
        );
    }
}

AgendaPreviewEventComponent.propTypes = {
    item: PropTypes.object,
    event: PropTypes.object,
    fetchEvent: PropTypes.func,
};

const mapStateToProps = (state, ownProps) => ({
    event: state.itemsById[ownProps.item.event_id],
});

const mapDispatchToProps = (dispatch) => ({
    fetchEvent: (eventId) => dispatch(fetchItem(eventId)),
});

export const AgendaPreviewEvent = connect(mapStateToProps, mapDispatchToProps)(AgendaPreviewEventComponent);
