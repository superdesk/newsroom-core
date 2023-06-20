import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {get} from 'lodash';
import {Tooltip} from 'bootstrap';

import {gettext} from 'utils';
import {isTouchDevice} from '../utils';
import NotificationListItem from './NotificationListItem';

class NotificationList extends React.Component<any, any> {
    static propTypes: any;
    tooltip: any;
    elem: any;

    constructor(props: any) {
        super(props);
        this.state = {
            displayItems: false,
            connected: false,
        };
        this.tooltip = null;
        this.elem = null;

        this.websocketConnected = this.websocketConnected.bind(this);
        this.websocketDisconnected = this.websocketDisconnected.bind(this);
        this.toggleDisplay = this.toggleDisplay.bind(this);
    }

    componentDidMount() {
        if (!isTouchDevice() && this.elem) {
            this.tooltip = new Tooltip(this.elem);
        }

        window.addEventListener('websocket:connected', this.websocketConnected);
        window.addEventListener('websocket:disconnected', this.websocketDisconnected);
    }

    componentWillUnmount() {
        if (this.elem && this.tooltip) {
            this.tooltip.dispose();
        }

        window.removeEventListener('websocket:connected', this.websocketConnected);
        window.removeEventListener('websocket:disconnected', this.websocketDisconnected);
    }

    websocketConnected() {
        this.setState({connected: true});
    }

    websocketDisconnected() {
        this.setState({connected: false});
    }

    componentDidUpdate(prevProps: any) {
        if (this.state.displayItems && this.props.count !== prevProps.count) {
            this.props.loadNotifications();
        }
    }

    toggleDisplay() {
        this.setState({displayItems:!this.state.displayItems});
        if (!this.state.displayItems) {
            this.props.loadNotifications();
            (document.getElementById('header-notification') as any).classList.add('notif--open');
        } else {
            (document.getElementById('header-notification') as any).classList.remove('notif--open');
        }
    }

    render() {
        return (
            <div className="badge--top-right">
                <h3 className="a11y-only">Notification Bell</h3>
                {this.props.count > 0 &&
                    <div className="badge rounded-pill">
                        {this.props.count}
                    </div>
                }

                <span
                    className={classNames(
                        'notif__circle',
                        {'notif__circle--disconnected': !this.state.connected}
                    )}
                    ref={(elem: any) => this.elem = elem}
                    title={gettext('Notifications')}>
                    <h3 className="a11y-only">Notification bell</h3>
                    <i className='icon--alert icon--white' onClick={this.toggleDisplay} />
                </span>

                {!this.state.displayItems ? null : this.props.count === 0 ? (
                    <div className="notif__list dropdown-menu dropdown-menu-right show">
                        <div className='notif__list__header d-flex'>
                            <span className='notif__list__header-headline ms-3'>{gettext('Notifications')}</span>
                        </div>
                        <div className='notif__list__message'>
                            {gettext('No new notifications!')}
                        </div>
                    </div>
                ) : (
                    <div className="notif__list dropdown-menu dropdown-menu-right show">
                        <div className='notif__list__header d-flex'>
                            <span className='notif__list__header-headline ms-3'>{gettext('Notifications')}</span>
                            <button
                                type="button"
                                className="button-pill ms-auto me-3"
                                onClick={this.props.clearAll}>{gettext('Clear All')}
                            </button>
                        </div>
                        {this.props.loading ? (
                            <div className='notif__list__message'>
                                {gettext('Loading...')}
                            </div>
                        ) : (
                            this.props.notifications.map((notification: any) => (
                                <NotificationListItem
                                    key={get(this.props.items, `${notification.item}._id`, 'test')}
                                    item={get(
                                        this.props.items,
                                        `${notification.item}`,
                                        get(notification, 'data.item', {})
                                    )}
                                    notification={notification}
                                    clearNotification={this.props.clearNotification}
                                />
                            ))
                        )}
                    </div>
                )}
            </div>
        );
    }
}

NotificationList.propTypes = {
    items: PropTypes.object,
    count: PropTypes.number,
    notifications: PropTypes.array,
    clearNotification: PropTypes.func,
    clearAll: PropTypes.func,
    loadNotifications: PropTypes.func,
    loading: PropTypes.bool,
};

export default NotificationList;
