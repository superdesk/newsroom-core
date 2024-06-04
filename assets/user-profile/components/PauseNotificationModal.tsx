import * as React from 'react';
import {connect} from 'react-redux';
import {IEvent, IUser} from 'interfaces';
import {gettext} from 'utils';
import {modalFormInvalid, modalFormValid} from 'actions';
import {updateUserNotificationSchedule} from 'user-profile/actions';
import Modal from 'components/Modal';

interface IProps {
    modalFormInvalid(): void;
    modalFormValid(): void;
    updateUserNotificationPause(schedule: Omit<IUser['notification_schedule'], 'last_run_time'>, message: string): void;
    data: {
        user: IUser;
    };
}

interface IState {
    pauseFrom: string;
    pauseTo: string;
}

const disabledOptionDateFrom = new Date().toISOString().split('T')[0];

const ONE_DAY = 1; // representing one day, can be used for adding or subtracting a day depending on the context of the function

const DATE_ID = 'date-from';

class PauseNotificationModalComponent extends React.Component<IProps, IState> {
    formRef: React.RefObject<HTMLFormElement>;
    constructor(props: IProps) {
        super(props);

        this.state = {
            pauseFrom: this.props.data.user.notification_schedule?.pauseFrom ?? '',
            pauseTo: this.props.data.user.notification_schedule?.pauseTo ?? '',
        };

        this.onSubmitForm = this.onSubmitForm.bind(this);
        this.updateDate = this.updateDate.bind(this);
        this.formRef = React.createRef<HTMLFormElement>();
    }

    componentDidMount() {
        this.props.modalFormValid();
    }

    onSubmitForm(event: React.FormEvent<HTMLFormElement>) {
        event.stopPropagation();
        event.preventDefault();

        if (this.formRef.current == null) {
            throw new Error('ref missing');
        }

        const inputs = this.formRef.current.querySelectorAll('input') as NodeListOf<HTMLInputElement>;

        const hasErrors = Array.from(inputs).some(input => {
            return input.checkValidity() !== true;
        });

        if (hasErrors === true) {
            this.formRef.current.reportValidity();
        } else {
            this.props.updateUserNotificationPause(this.state, gettext('Notifications paused'));
        }
    }

    updateDate(event: React.ChangeEvent<HTMLInputElement>, pauseType: 'pauseFrom' | 'pauseTo') {
        this.setState({...this.state, [pauseType]: event.target.value});
    }

    disabledPrevOptions(state: string | undefined) {
        if (state != '' && state != undefined) {
            const newMaxDate = new Date(state);
            newMaxDate.setDate(newMaxDate.getDate() + ONE_DAY);
            return newMaxDate.toISOString().split('T')[0];
        } else {
            return disabledOptionDateFrom;
        }
    }

    disabledNextOptions(state: string | undefined) {
        if (state != '' && state != undefined) {
            const newMaxDate = new Date(state);
            newMaxDate.setDate(newMaxDate.getDate() - ONE_DAY);
            return newMaxDate.toISOString().split('T')[0];
        }
    }

    render() {
        return (
            <Modal
                onSubmit={() => {
                    this.formRef.current?.dispatchEvent(new Event('submit', {cancelable: true, bubbles: true}));
                }}
                title={gettext('Pause notifications...')}
                onSubmitLabel={gettext('Pause notifications')}
                disableButtonOnSubmit={false}
                className="edit-schedule__modal"
            >
                <div className="nh-container nh-container--highlight rounded--none">
                    <form
                        ref={this.formRef}
                        onSubmit={(event) => this.onSubmitForm(event)}
                    >
                        <div className='d-flex align-items-center gap-5'>
                            <div className="d-flex flex-column align-items-start">
                                <label htmlFor={DATE_ID}>{gettext('From')}</label>
                                <input
                                    id={DATE_ID}
                                    type="date"
                                    name={DATE_ID}
                                    className="form-control"
                                    onChange={(event) => {
                                        this.updateDate(event, 'pauseFrom');
                                    }}
                                    value={this.state.pauseFrom}
                                    min={disabledOptionDateFrom}
                                    max={this.disabledNextOptions(this.state.pauseTo)}
                                />
                            </div>

                            <div className="d-flex flex-column align-items-start">
                                <label htmlFor="date-to">{gettext('To')}</label>
                                <input
                                    id="date-to"
                                    type="date"
                                    name="date-to"
                                    className="form-control"
                                    onChange={(event) => {
                                        this.updateDate(event, 'pauseTo');
                                    }}
                                    value={this.state.pauseTo}
                                    min={this.disabledPrevOptions(this.state.pauseFrom)}
                                />
                            </div>
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
    updateUserNotificationPause: (schedule: Omit<IUser['notification_schedule'], 'last_run_time'>, message: string) => (
        dispatch(updateUserNotificationSchedule(schedule, message))
    ),
});

export const PauseNotificationModal = connect(
    null,
    mapDispatchToProps,
)(PauseNotificationModalComponent);
