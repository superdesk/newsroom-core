import * as React from 'react';
import {connect} from 'react-redux';
import moment from 'moment-timezone';

import {IUser} from 'interfaces';
import {gettext, getScheduledNotificationConfig, TIME_FORMAT_24_HOUR_CLOCK} from 'utils';
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

interface IAddButton {
    type: 'add'
}

interface IRemoveButton {
    type: 'remove';
    index: number;
}

type IButtonType = IAddButton | IRemoveButton;


interface IState {
    timezone: string;
    times: Array<string>;
}

const minutes = Array.from(Array(60).keys());
const disabledMinutes: Array<number> = minutes.filter((num) => num % 15 !== 0);

class EditNotificationScheduleModalComponent extends React.Component<IProps, IState> {
    formRef: React.RefObject<HTMLFormElement>;
    private TIME_FORMAT: '24-hours' | '12-hours';
    constructor(props: IProps) {
        super(props);

        this.state = {
            timezone: this.props.data.user.notification_schedule?.timezone ?? moment.tz.guess(),
            times: this.props.data.user.notification_schedule?.times ?? getScheduledNotificationConfig().default_times,
        };

        this.onSubmitForm = this.onSubmitForm.bind(this);
        this.formRef = React.createRef<HTMLFormElement>();

        this.TIME_FORMAT = TIME_FORMAT_24_HOUR_CLOCK ? '24-hours' : '12-hours';
    }

    componentDidMount() {
        this.props.modalFormValid();
    }

    updateTime(newTime: string, index: number) {
        this.setState((prevState) => {
            const times = [...prevState.times];

            times[index] = newTime;

            return {times};
        });
    }

    updateNumberPerDay(props: IButtonType) {
        const times = [...this.state.times];        

        if (props.type === 'add') {
            times.push(this.state.times[this.state.times.length - 1]);
        } else {
            times.splice(props.index, 1);
        }

        this.setState({
            times: [...times]
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
                        <div className='d-flex flex-column align-items-center'>
                            <div className="form-group schedule-times__input-container d-flex justify-content-center">
                                {this.state.times.map((_time, index) => {
                                    return (
                                        <div className='d-flex flex-column align-items-center gap-2' key={index}>
                                            <TimePicker
                                                value={this.state.times[index]}
                                                disabledOptions={{
                                                    minutes: disabledMinutes,
                                                }}
                                                onChange={(value) => {
                                                    this.updateTime(value, index);
                                                }}
                                            />
                                            <button
                                                type='button'
                                                className="icon-button icon-button--mini icon-button--secondary icon-button--bordered"
                                                data-test-id="remove-schedule"
                                                aria-label={gettext('Remove schedule')}
                                                disabled={this.state.times.length < 2}
                                                onClick={() => this.updateNumberPerDay({type: 'remove', index})}
                                            >
                                                <i className="icon--minus" />
                                            </button>
                                        </div>
                                    );
                                })}
                                {this.state.times.length < 3 && (
                                    <button
                                        type='button'
                                        className="icon-button icon-button--secondary icon-button--bordered"
                                        data-test-id="add-schedule"
                                        aria-label={gettext('Add schedule')}
                                        onClick={() => this.updateNumberPerDay({type:'add'})}
                                    >
                                        <i className="icon--plus" />
                                    </button>
                                )}  
                            </div>
                            <TimezoneInput
                                name="timezone"
                                label={gettext('Timezone')}
                                onChange={(event) => {
                                    this.setState({timezone: event.target.value});
                                }}
                                value={this.state.timezone}
                            />
                        </div>
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
