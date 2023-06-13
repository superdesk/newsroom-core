import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {
    deleteNotification,
    deleteAllNotifications,
    loadNotifications,
} from '../actions';

import NotificationList from 'components/NotificationList';

class NotificationsApp extends React.Component<any, any> {
    constructor(props: any, context: any) {
        super(props, context);
    }

    render() {
        return [
            <NotificationList
                key="notifications"
                notifications={this.props.notifications}
                items={this.props.items}
                count={this.props.count}
                clearNotification={this.props.clearNotification}
                clearAll={this.props.clearAll}
                loadNotifications={this.props.loadNotifications}
                loading={this.props.loading}
            />,
        ];
    }
}

NotificationsApp.propTypes = {
    user: PropTypes.string,
    items: PropTypes.object,
    notifications: PropTypes.arrayOf(PropTypes.object),
    count: PropTypes.number,
    clearNotification: PropTypes.func,
    clearAll: PropTypes.func,
    loadNotifications: PropTypes.func,
    loading: PropTypes.bool,
};

const mapStateToProps = (state: any) => ({
    user: state.user,
    items: state.items,
    notifications: state.notifications,
    count: state.notificationCount,
    loading: state.loading,
});

const mapDispatchToProps = (dispatch: any) => ({
    clearNotification: (id: any) => dispatch(deleteNotification(id)),
    clearAll: () => dispatch(deleteAllNotifications()),
    loadNotifications: () => dispatch(loadNotifications()),
});

export default connect(mapStateToProps, mapDispatchToProps)(NotificationsApp);
