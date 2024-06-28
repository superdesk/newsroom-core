import React from 'react';
import classNames from 'classnames';
import {Tooltip} from 'bootstrap';
import {gettext} from 'utils';
import {isTouchDevice} from '../utils';
import {NotificationPopup, IProps as INotificationPopupProps} from './NotificationPopup';

interface IState {
    displayItems: boolean;
    connected: boolean;
}

type IProps = INotificationPopupProps;

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
        this.setState({displayItems: !this.state.displayItems}, (() => {
            if (this.state.displayItems) {
                this.props.loadNotifications();
                (document.getElementById('header-notification') as HTMLElement).classList.add('navbar-notifications--open');
            } else {
                (document.getElementById('header-notification') as HTMLElement).classList.remove('navbar-notifications--open');
            }
        }));
    }

    render() {
        
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

                {this.state.displayItems === true && (
                    <NotificationPopup
                        fullUser={this.props.fullUser}
                        items={this.props.items}
                        count={this.props.count}
                        notifications={this.props.notifications}
                        loading={this.props.loading}
                        clearNotification={this.props.clearNotification}
                        clearAll={this.props.clearAll}
                        loadNotifications={this.props.loadNotifications}
                        resumeNotifications={this.props.resumeNotifications}
                    />
                )}
            </div>
        );
    }
}

export default NotificationList;
