import * as React from 'react';
import {connect} from 'react-redux';
import moment from 'moment-timezone';

import {IUser} from 'interfaces';
import {gettext, getScheduledNotificationConfig} from 'utils';
import {modalFormInvalid, modalFormValid} from 'actions';
import {updateUserNotificationSchedules} from 'user-profile/actions';

import Modal from 'components/Modal';
import {TimezoneInput} from 'components/TimezoneInput';
import {TimePicker} from 'components/cards/TimePicker';

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

const minutes = Array.from(Array(60).keys());
const changedMinutes: Array<number> = minutes.filter((num) => num % 15 !== 0);

class EditNotificationScheduleModalComponent extends React.Component<IProps, IState> {
    formRef: React.RefObject<HTMLFormElement>;
    constructor(props: IProps) {
        super(props);

        this.state = {
            timezone: this.props.data.user.notification_schedule?.timezone ?? moment.tz.guess(),
            times: this.props.data.user.notification_schedule?.times ?? getScheduledNotificationConfig().default_times,
        };

        this.onSubmitForm = this.onSubmitForm.bind(this);
        this.formRef = React.createRef<HTMLFormElement>();
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

    onSubmitForm(event: React.FormEvent<HTMLFormElement>) {
        event.stopPropagation();
        event.preventDefault();

        if (this.formRef.current == null) {
            throw new Error('ref missing');
        }

        const inputs = this.formRef.current.querySelectorAll('input') as NodeListOf<HTMLInputElement>;

        const hasErrors = [...inputs].some(input => {
            return input.checkValidity() !== true;
        });

        if (hasErrors === true) {
            this.formRef.current.reportValidity();
        } else {
            this.props.updateUserNotificationSchedules(this.state);
        }
    }

    render() {
        return (
            <Modal
                onSubmit={() => {
                    this.formRef.current?.dispatchEvent(new Event('submit', {cancelable: true, bubbles: true}));
                }}
                title={gettext('Edit global notifications schedule')}
                onSubmitLabel={gettext('Save')}
                disableButtonOnSubmit={false}
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
                    <form
                        ref={this.formRef}
                        onSubmit={(event) => this.onSubmitForm(event)}
                    >
                        <div className="form-group schedule-times__input-container">
                            <TimePicker
                                value={this.state.times[0]}
                                disabledOptions={{
                                    minutes: changedMinutes,
                                }}
                                onChange={(value) => {
                                    this.updateTime(value, 0);
                                }}
                            />
                            <TimePicker
                                value={this.state.times[1]}
                                disabledOptions={{
                                    minutes: changedMinutes,
                                }}
                                onChange={(value) => {
                                    this.updateTime(value, 1);
                                }}
                            />
                            <TimePicker
                                value={this.state.times[2]}
                                disabledOptions={{
                                    minutes: changedMinutes,
                                }}
                                onChange={(value) => {
                                    this.updateTime(value, 2);
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
