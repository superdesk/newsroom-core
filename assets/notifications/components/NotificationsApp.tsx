import React from 'react';
import {connect} from 'react-redux';
import {
    deleteNotification,
    deleteAllNotifications,
    loadNotifications,
    updateFullUser,
} from '../actions';
import {store as userProfileStore} from '../../user-profile/store';
import {getUser as getUserProfileUser} from 'user-profile/actions';
import NotificationList from 'components/NotificationList';
import {postNotificationSchedule} from 'helpers/notification';
import {gettext} from 'utils';
import {IUser} from 'interfaces/user';

interface IProps {
    fullUser: IUser;
    items: any;
    notifications: Array<any>;
    count: number;
    loading: boolean;
    clearNotification(id: IUser['_id']): void;
    clearAll(): void;
    loadNotifications(): void;
    updateUser(id: IUser['_id']): void;
}

class NotificationsApp extends React.Component<IProps, any> {
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
                fullUser={this.props.fullUser}
                resumeNotifications={() => {
                    postNotificationSchedule(this.props.fullUser._id, {pauseFrom: '', pauseTo: ''}, gettext('Notifications resumed')).then(() =>
                        this.props.updateUser(this.props.fullUser._id)
                    );
                }}
            />,
        ];
    }
}

const mapStateToProps = (state: any) => ({
    fullUser: state.fullUser,
    items: state.items,
    notifications: state.notifications,
    count: state.notificationCount,
    loading: state.loading,
});

const mapDispatchToProps = (dispatch: any) => ({
    clearNotification: (id: any) => dispatch(deleteNotification(id)),
    clearAll: () => dispatch(deleteAllNotifications()),
    loadNotifications: () => dispatch(loadNotifications()),
    updateUser: (userId: string) => {
        dispatch(updateFullUser(userId)).then((fullUser: IUser) => {
            userProfileStore.dispatch(getUserProfileUser(fullUser));
        });
    }
});

export default connect(mapStateToProps, mapDispatchToProps)(NotificationsApp);
