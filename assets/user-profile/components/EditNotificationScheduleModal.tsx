import * as React from 'react';
import {connect} from 'react-redux';
import moment from 'moment-timezone';

import {IUser} from 'interfaces';
import {gettext, getScheduledNotificationConfig} from 'utils';
import {modalFormInvalid, modalFormValid} from 'actions';
import {updateUserNotificationSchedules} from 'user-profile/actions';

import Modal from 'components/Modal';
import {TimezoneInput} from 'components/TimezoneInput';

interface IProps {
    modalFormInvalid(): void;
    modalFormValid(): void;
    updateUserNotificationSchedules(schedule: Omit<IUser['notification_schedule'], 'last_run_time'>): void;
    data: {
        user: IUser;
    };
}

interface IState {
    timezone: string;
    times: Array<string>;
}


class EditNotificationScheduleModalComponent extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {
            timezone: this.props.data.user.notification_schedule?.timezone ?? moment.tz.guess(),
            times: this.props.data.user.notification_schedule?.times ?? getScheduledNotificationConfig().default_times,
        };
    }

    componentDidMount() {
        this.props.modalFormValid();
    }

    updateTime(newTime: string, index: number) {
        this.setState((prevState) => {
            const times = [...prevState.times];

            times[index] = newTime;

            return {times: times.sort()};
        });
    }

    render() {
        return (
            <Modal
                onSubmit={() => this.props.updateUserNotificationSchedules(this.state)}
                title={gettext('Edit global notifications schedule')}
                onSubmitLabel={gettext('Save')}
                disableButtonOnSubmit={true}
                className="edit-schedule__modal"
            >
                <div className="nh-container nh-container--highlight rounded--none">
                    <p className="nh-container__text--small">
                        {gettext(
                            'Editing the global notifications schedule will adjust the ' +
                            'timing and frequency of all topic notifications sent to you.'
                        )}
                    </p>
                    <div className="h-spacer h-spacer--medium"/>
                    <span className="nh-container__schedule-info form-label">
                        {gettext('Daily, at:')}
                    </span>
                    <form>
                        <div className="form-group schedule-times__input-container">
                            <input
                                type="time"
                                value={this.state.times[0]}
                                onChange={(event) => {
                                    this.updateTime(event.target.value, 0);
                                }}
                            />
                            <input
                                type="time"
                                value={this.state.times[1]}
                                onChange={(event) => {
                                    this.updateTime(event.target.value, 1);
                                }}
                            />
                            <input
                                type="time"
                                value={this.state.times[2]}
                                onChange={(event) => {
                                    this.updateTime(event.target.value, 2);
                                }}
                            />
                        </div>
                        <TimezoneInput
                            name="timezone"
                            label={gettext('Timezone')}
                            onChange={(event) => {
                                this.setState({timezone: event.target.value});
                            }}
                            value={this.state.timezone}
                        />
                    </form>
                </div>
            </Modal>
        );
    }
}

const mapDispatchToProps = (dispatch: any) => ({
    modalFormInvalid: () => dispatch(modalFormInvalid()),
    modalFormValid: () => dispatch(modalFormValid()),
    updateUserNotificationSchedules: (schedule: Omit<IUser['notification_schedule'], 'last_run_time'>) => (
        dispatch(updateUserNotificationSchedules(schedule))
    ),
});

export const EditNotificationScheduleModal = connect(
    null,
    mapDispatchToProps,
)(EditNotificationScheduleModalComponent);
