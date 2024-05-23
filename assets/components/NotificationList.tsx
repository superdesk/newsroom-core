import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {get} from 'lodash';
import {Tooltip} from 'bootstrap';
import {formatDate, gettext} from 'utils';
import {isTouchDevice} from '../utils';
import NotificationListItem from './NotificationListItem';
import {postNotificationSchedule} from 'user-profile/actions';

interface IState {
    displayItems: boolean;
    connected: boolean;
}

class NotificationList extends React.Component<any, IState> {
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
        this.setState({displayItems: !this.state.displayItems});
        if (!this.state.displayItems) {
            this.props.loadNotifications();
            (document.getElementById('header-notification') as HTMLElement).classList.add('navbar-notifications--open');
        } else {
            (document.getElementById('header-notification') as HTMLElement).classList.remove('navbar-notifications--open');
        }
    }

    render() {
        const notificationPopUp = () => {
            if (this.props.fullUser.notification_schedule?.pauseFrom != '' && this.props.fullUser.notification_schedule?.pauseFrom != '') {
                return (
                    <div className="notif__list dropdown-menu dropdown-menu-right show">
                        <div className='notif__list__header d-flex'>
                            <span className='notif__list__header-headline ms-3'>{gettext('Notifications')}</span>
                        </div>

                        <div className='d-flex flex-column gap-2 p-3'>
                            <div className='nh-container nh-container__text--alert p-2'>
                                {gettext('All notifications are paused until {{pauseTo}}', {pauseTo: formatDate(this.props.fullUser.notification_schedule?.pauseTo)})}
                            </div>

                            <button
                                type="button"
                                className="nh-button nh-button--small nh-button--tertiary"
                                onClick={() => {
                                    postNotificationSchedule(this.props.user, {pauseFrom: '', pauseTo: ''}).then(() =>
                                        this.props.updateUserNotificationPause()                          
                                    );
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

                        <div className='p-3'>
                            <div className='nh-container nh-container__text--info p-2'>
                                {gettext('All notifications are set to be paused from {{pauseFrom}} to {{pauseTo}}', {pauseFrom: formatDate(this.props.fullUser.notification_schedule?.pauseFrom), pauseTo: formatDate(this.props.fullUser.notification_schedule?.pauseTo)})}
                            </div>
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
                    </div>;
                }
            }
        };
        
        return (
            <div className="navbar-notifications__inner">
                <h3 className="a11y-only">Notification Bell</h3>
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
                    <h3 className="a11y-only">{gettext('Notification bell')}</h3>
                    <i className='icon--alert' onClick={this.toggleDisplay} />
                </span>

                {this.state.displayItems && notificationPopUp()}
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
