import React from 'react';
import classNames from 'classnames';
import {get} from 'lodash';
import {Tooltip} from 'bootstrap';
import {formatDate, gettext} from 'utils';
import {isTouchDevice} from '../utils';
import NotificationListItem from './NotificationListItem';
import {IUser} from 'interfaces';

interface IState {
    displayItems: boolean;
    connected: boolean;
}

interface IProps {
    items: any;
    count: number;
    fullUser: IUser;
    notifications: Array<any>;
    loading: boolean;
    clearNotification(id: IUser['_id']): void;
    clearAll(): void;
    loadNotifications(): void;
    resumeNotifications(): void;
}

class NotificationList extends React.Component<IProps, IState> {
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
        this.setState({displayItems: !this.state.displayItems});
        if (!this.state.displayItems) {
            this.props.loadNotifications();
            (document.getElementById('header-notification') as HTMLElement).classList.add('navbar-notifications--open');
        } else {
            (document.getElementById('header-notification') as HTMLElement).classList.remove('navbar-notifications--open');
        }
    }

    render() {
        const notificationArePaused: boolean = new Date(this.props.fullUser.notification_schedule?.pauseFrom ?? '') < new Date();
        
        return (
            <div className="navbar-notifications__inner">
                <h3 className="a11y-only">{gettext('Notifications')}</h3>
                {this.props.count > 0 &&
                    <div className="navbar-notifications__badge">
                        {this.props.count}
                    </div>
                }

                <span
                    className={classNames(
                        'navbar-notifications__inner-circle',
                        {'navbar-notifications__inner-circle--disconnected': !this.state.connected}
                    )}
                    ref={(elem: any) => this.elem = elem}
                    title={gettext('Notifications')}
                >
                    <h3 className="a11y-only">{gettext('Notifications')}</h3>
                    <i className='icon--alert' onClick={this.toggleDisplay} />
                </span>

                {(() => {
                    if (this.state.displayItems !== true) {
                        return null;
                    }

                    if (this.props.fullUser.notification_schedule != null && this.props.fullUser.notification_schedule.pauseFrom != '' && this.props.fullUser.notification_schedule.pauseTo != '' && notificationArePaused) {
                        return (
                            <div className="notif__list dropdown-menu dropdown-menu-right show">
                                <div className='notif__list__header d-flex'>
                                    <span className='notif__list__header-headline ms-3'>{gettext('Notifications')}</span>
                                </div>
        
                                <div className='d-flex flex-column gap-2 p-3'>
                                    <div className='nh-container nh-container__text--alert p-2'>
                                        {gettext('All notifications are paused until {{date}}', {date: formatDate(this.props.fullUser.notification_schedule.pauseTo)})}
                                    </div>
        
                                    <button
                                        type="button"
                                        className="nh-button nh-button--small nh-button--tertiary"
                                        onClick={() => {
                                            this.props.resumeNotifications();
                                        }}
                                    >
                                        {gettext('Resume all notifications')}
                                    </button>
                                </div>
                            </div>
                        );
                    } else {
                        if (this.props.count === 0) {
                            return (
                                <div className="notif__list dropdown-menu dropdown-menu-right show">
                                    <div className='notif__list__header d-flex'>
                                        <span className='notif__list__header-headline ms-3'>{gettext('Notifications')}</span>
                                    </div>
        
                                    <div className='notif__list__message'>
                                        {gettext('No new notifications!')}
                                    </div>
                                </div>
                            );
                        } else {
                            <div className="notif__list dropdown-menu dropdown-menu-right show">
                                <div className='notif__list__header d-flex'>
                                    <span className='notif__list__header-headline ms-3'>{gettext('Notifications')}</span>
        
                                    <button
                                        type="button"
                                        className="button-pill ms-auto me-3"
                                        onClick={this.props.clearAll}
                                    >
                                        {gettext('Clear All')}
                                    </button>
                                </div>

                                {(this.props.fullUser.notification_schedule != null && this.props.fullUser.notification_schedule.pauseFrom != '' && this.props.fullUser.notification_schedule.pauseTo != '' && !notificationArePaused) && (
                                    <div className='p-3'>
                                        <div className='nh-container nh-container__text--info p-2'>
                                            {gettext('All notifications are set to be paused from {{dateFrom}} to {{dateTo}}', {dateFrom: formatDate(this.props.fullUser.notification_schedule.pauseFrom), dateTo: formatDate(this.props.fullUser.notification_schedule.pauseTo)})}
                                        </div>
                                    </div>
                                )}
        
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
                            </div>;
                        }
                    }})()
                }
            </div>
        );
    }
}

export default NotificationList;
