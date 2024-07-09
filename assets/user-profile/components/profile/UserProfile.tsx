import React from 'react';
import {connect} from 'react-redux';

import {IUser} from 'interfaces';
import {gettext, getSubscriptionTimesString, formatDate, parseISODate, notificationsArePaused, notificationsWillBePaused} from 'utils';

import TextInput from 'components/TextInput';
import SelectInput from 'components/SelectInput';
import CheckboxInput from 'components/CheckboxInput';
import {getLocaleInputOptions, getDefaultLocale} from 'users/utils';

import {
    fetchUser,
    editUser,
    saveUser,
    setError,
    openEditTopicNotificationsModal,
    openPauseNotificationModal,
    updateUserNotificationSchedule,
} from '../../actions';
import {IUserProfileState} from 'user-profile/reducers';
import {IUserProfileUpdates} from 'interfaces/user';

interface IProps {
    user: IUser;
    errors: {[field in keyof IUserProfileUpdates]: string[]};
    onChange(updates: IUserProfileUpdates): void;
    saveUser(): void;
    setError(errors: {[key: string]: string}): void;
    fetchUser(userId: IUser['_id']): void;
    openEditTopicNotificationsModal(): void;
    openPauseNotificationModal(): void;
    authProviderFeatures: IUserProfileState['authProviderFeatures'];
    updateUserNotificationPause(schedule: Omit<IUser['notification_schedule'], 'last_run_time'>, message: string): void;
}

class UserProfile extends React.PureComponent<IProps> {
    static propTypes: any;
    constructor(props: any) {
        super(props);
        this.save = this.save.bind(this);
    }

    isFormValid() {
        let valid = true;
        const errors: any = {};

        if (!this.props.user.first_name) {
            errors.first_name = [gettext('Please provide first name')];
            valid = false;
        }

        if (!this.props.user.last_name) {
            errors.last_name = [gettext('Please provide last name')];
            valid = false;
        }

        this.props.setError(errors);
        return valid;
    }

    save(event: any) {
        event.preventDefault();

        if (!this.isFormValid()) {
            return;
        }

        this.props.saveUser();
    }

    render() {
        const {user, onChange, errors, authProviderFeatures} = this.props;
        const onCancel = () => this.props.fetchUser(this.props.user._id);
        const localeOptions = getLocaleInputOptions();
        const pausedFrom = parseISODate(this.props.user.notification_schedule?.pause_from);
        const pausedTo = parseISODate(this.props.user.notification_schedule?.pause_to);
        return (
            <form className="profile-content profile-content--user">
                <div className="profile-content__main">
                    <div className="profile-content__main-inner col-12 mx-auto pt-3">
                        <div className="row">
                            <div className="col-lg-6">
                                <TextInput
                                    name='first_name'
                                    label={gettext('First Name')}
                                    value={user.first_name}
                                    onChange={(event) => onChange({first_name: event.target.value})}
                                    error={errors?.first_name} />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='last_name'
                                    label={gettext('Last Name')}
                                    value={user.last_name}
                                    onChange={(event) => onChange({last_name: event.target.value})}
                                    error={errors?.last_name} />
                            </div>

                            <div className="col-lg-12">
                                <TextInput
                                    name='email'
                                    label={gettext('Email')}
                                    value={user.email}
                                    readOnly
                                />
                            </div>

                            {authProviderFeatures?.change_password === true && (
                                <div className="col-lg-12">
                                    <div className="form-group">
                                        <a
                                            href="/change_password"
                                            className="nh-button nh-button--small nh-button--tertiary"
                                        >
                                            {gettext('Change password')}
                                        </a>
                                    </div>
                                </div>
                            )}

                            <div className="col-lg-6">
                                <TextInput
                                    name='phone'
                                    label={gettext('Phone')}
                                    value={user.phone}
                                    onChange={(event) => onChange({phone: event.target.value})}
                                    error={errors?.phone} />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='mobile'
                                    label={gettext('Mobile')}
                                    value={user.mobile}
                                    onChange={(event) => onChange({mobile: event.target.value})}
                                    error={errors?.mobile} />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='role'
                                    label={gettext('Role')}
                                    value={user.role}
                                    onChange={(event) => onChange({role: event.target.value})}
                                    error={errors?.role} />
                            </div>

                            <div className="col-lg-12 mb-2">
                                <CheckboxInput
                                    name='receive_app_notifications'
                                    label={gettext('Receive App Notifications')}
                                    value={!!user.receive_app_notifications}
                                    onChange={(event) => onChange({receive_app_notifications: event.target.checked})}
                                />
                            </div>

                            <div className="col-lg-12">
                                <CheckboxInput
                                    name='receive_email'
                                    label={gettext('Receive Email Notifications')}
                                    value={!!user.receive_email}
                                    onChange={(event) => onChange({receive_email: event.target.checked})}
                                />
                            </div>

                            <div className="col-lg-6">
                                <div className="nh-container nh-container--highlight mb-1 mt-3">
                                    <p className="nh-container__text--small">
                                        {gettext('You will receive email notifications daily, sent in a digest ' +
                                            'format at regular intervals. This setting will apply to all subscribed ' +
                                            'scheduled email notifications (e.g. {{ wire }} Topics, ' +
                                            '{{ agenda }} Topics).', window.sectionNames)}
                                    </p>
                                    <div className="h-spacer h-spacer--medium" />
                                    <span className="nh-container__schedule-info mb-3">
                                        {getSubscriptionTimesString(user)}
                                    </span>
                                    <button
                                        type="button"
                                        className="nh-button nh-button--small nh-button--tertiary"
                                        onClick={this.props.openEditTopicNotificationsModal}
                                    >
                                        {gettext('Edit schedule')}
                                    </button>
                                </div>
                            </div>
                            
                            <div className='row'>
                                <div className="col-lg-6">
                                    {(notificationsArePaused(pausedFrom, pausedTo) || notificationsWillBePaused(pausedFrom, pausedTo)) ?
                                        (
                                            <div className="nh-container nh-container__text--alert">
                                                <div className='d-flex flex-column gap-3 p-3'>
                                                    <div>
                                                        {gettext('All notifications will be paused from {{dateFrom}} to {{dateTo}}', {dateFrom: formatDate(pausedFrom), dateTo: formatDate(pausedTo)})}
                                                    </div>
                                                    <div>
                                                        <button
                                                            type="button"
                                                            className="nh-button nh-button--small nh-button--tertiary"
                                                            onClick={() => {
                                                                this.props.updateUserNotificationPause({pause_from: '', pause_to: ''}, gettext('Notifications resumed'));
                                                            }}
                                                        >
                                                            {gettext('Clear Pausing')}
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        )
                                        : (
                                            <div className="nh-container nh-container--highlight mb-3 mt-1">
                                                <button
                                                    type="button"
                                                    className="nh-button nh-button--small nh-button--tertiary"
                                                    onClick={this.props.openPauseNotificationModal}
                                                >
                                                    {gettext('Pause All Notifications')}
                                                </button>
                                            </div>
                                        )
                                    }
                                </div>
                            </div>

                            <div className="col-lg-12"></div>


                            {!!localeOptions.length &&
                                <div className="col-lg-6">
                                    <SelectInput
                                        name='locale'
                                        label={gettext('Language')}
                                        value={user.locale}
                                        onChange={(event) => onChange({locale: event.target.value})}
                                        options={localeOptions}
                                        defaultOption={getDefaultLocale()}
                                    />
                                </div>
                            }
                        </div>
                    </div>
                </div>

                <div className='profile-content__footer'>
                    <input
                        type='button'
                        className='nh-button nh-button--secondary'
                        value={gettext('Cancel')}
                        onClick={onCancel} />

                    <input
                        type='button'
                        className='nh-button nh-button--primary'
                        value={gettext('Save Changes')}
                        onClick={this.save} />
                </div>
            </form>
        );
    }
}

const mapStateToProps = (state: IUserProfileState) => ({
    user: state.editedUser,
    errors: state.errors ?? {},
    authProviderFeatures: state.authProviderFeatures,
});

const mapDispatchToProps = (dispatch: any) => ({
    saveUser: () => dispatch(saveUser()),
    fetchUser: (userId: IUser['_id']) => dispatch(fetchUser(userId)),
    onChange: (updates: IUserProfileUpdates) => dispatch(editUser(updates)),
    setError: (errors: {[key: string]: string}) => dispatch(setError(errors)),
    openEditTopicNotificationsModal: () => dispatch(openEditTopicNotificationsModal()),
    openPauseNotificationModal: () => dispatch(openPauseNotificationModal()),
    updateUserNotificationPause: (schedule: Omit<IUser['notification_schedule'], 'last_run_time'>, message: string) => (
        dispatch(updateUserNotificationSchedule(schedule, message))
    ),
});

export default connect(mapStateToProps, mapDispatchToProps)(UserProfile);
