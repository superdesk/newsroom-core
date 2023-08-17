import React from 'react';
import {connect} from 'react-redux';

import {IUser} from 'interfaces';
import {gettext, getSubscriptionTimesString} from 'utils';

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
} from '../../actions';

interface IProps {
    user: IUser;
    errors: {[key: string]: string};
    onChange(event: React.ChangeEvent): void;
    saveUser(): void;
    setError(errors: {[key: string]: string}): void;
    fetchUser(userId: IUser['_id']): void;
    openEditTopicNotificationsModal(): void;
}

class UserProfile extends React.Component<IProps, any> {
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
        const {user, onChange, errors} = this.props;
        const onCancel = () => this.props.fetchUser(this.props.user._id);
        const localeOptions = getLocaleInputOptions();
        return (
            <form className="profile-content profile-content--user">
                <div className="profile-content__main">
                    <div className="col-12 col-xl-10 mx-auto">
                        <div className="row pt-xl-4 pt-3 px-4">
                            <div className="col-lg-6">
                                <TextInput
                                    name='first_name'
                                    label={gettext('First Name')}
                                    value={user.first_name}
                                    onChange={onChange}
                                    error={errors ? errors.first_name : null} />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='last_name'
                                    label={gettext('Last Name')}
                                    value={user.last_name}
                                    onChange={onChange}
                                    error={errors ? errors.last_name : null} />
                            </div>

                            <div className="col-lg-12">
                                <TextInput
                                    name='email'
                                    label={gettext('Email')}
                                    value={user.email}
                                    readOnly
                                />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='phone'
                                    label={gettext('Phone')}
                                    value={user.phone}
                                    onChange={onChange}
                                    error={errors ? errors.phone : null} />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='mobile'
                                    label={gettext('Mobile')}
                                    value={user.mobile}
                                    onChange={onChange}
                                    error={errors ? errors.mobile : null} />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='role'
                                    label={gettext('Role')}
                                    value={user.role}
                                    onChange={onChange}
                                    error={errors ? errors.role : null} />
                            </div>

                            <div className="col-lg-12">
                                <CheckboxInput
                                    name='receive_app_notifications'
                                    label={gettext('Receive inApp notifications')}
                                    value={!!user.receive_app_notifications}
                                    onChange={onChange}
                                />
                            </div>

                            <div className="col-lg-12">
                                <CheckboxInput
                                    name='receive_email'
                                    label={gettext('Receive email notifications')}
                                    value={!!user.receive_email}
                                    onChange={onChange}
                                />
                            </div>

                            <div className="ng-flex__row">
                                <div className="col-lg-6">
                                    <div className="nh-container nh-container--highlight mb-3">
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
                            </div>

                            {!!localeOptions.length &&
                                <div className="col-lg-6">
                                    <SelectInput
                                        name='locale'
                                        label={gettext('Language')}
                                        value={user.locale}
                                        onChange={onChange}
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

const mapStateToProps = (state: any) => ({
    user: state.editedUser,
    errors: state.errors ?? {},
});

const mapDispatchToProps = (dispatch: any) => ({
    saveUser: () => dispatch(saveUser()),
    fetchUser: (userId: IUser['_id']) => dispatch(fetchUser(userId)),
    onChange: (event: React.ChangeEvent) => dispatch(editUser(event)),
    setError: (errors: {[key: string]: string}) => dispatch(setError(errors)),
    openEditTopicNotificationsModal: () => dispatch(openEditTopicNotificationsModal()),
});

export default connect(mapStateToProps, mapDispatchToProps)(UserProfile);
