import React from 'react';
import {get} from 'lodash';
import {connect} from 'react-redux';
import {Modal as BSModal} from 'bootstrap';

import {gettext} from 'utils';
import {closeModal} from 'actions';

import CloseButton from './CloseButton';
import classNames from 'classnames';

interface IButtonProps {
    label: string;
    type?: React.ButtonHTMLAttributes<HTMLButtonElement>['type'];
    onClick?(event: React.MouseEvent<HTMLButtonElement>): void;
}

/**
 * Primary modal button for actions like save/send/etc
 */
function ModalPrimaryButton({label, type, onClick, disabled}: IButtonProps & {disabled?: boolean}): React.ReactElement {
    assertButtonHandler(label, type, onClick);
    return (
        <button
            type={type || 'button'}
            onClick={onClick}
            className="nh-button nh-button--primary"
            disabled={disabled}
        >{label}</button>
    );
}

/**
 * Secondary modal button for actions like cancel/reset
 */
export function ModalSecondaryButton({label, type, onClick}: IButtonProps): React.ReactElement {
    assertButtonHandler(label, type, onClick);
    return (
        <button
            type={type || 'button'}
            onClick={onClick}
            className="nh-button nh-button--secondary"
        >{label}</button>
    );
}

/**
 * Test if button makes any sense
 *
 * either type or onClick handler must be specified
 */
function assertButtonHandler(label: IButtonProps['label'], type: IButtonProps['type'], onClick: IButtonProps['onClick']) {
    if (!type && !onClick) {
        console.warn('You should use either type or onClick handler for button', label);
    }
}

interface IProps {
    title: string;
    children: React.ReactNode | Array<React.ReactNode>;
    onSubmitLabel?: string; // defaults to 'Save'
    onCancelLabel: string; // defaults to 'Cancel'
    disableButtonOnSubmit?: boolean;
    clickOutsideToClose?: boolean; // defaults to false
    width?: 'full';
    className?: string;
    formValid: boolean; // provided by Redux state
    onSubmit(event: React.MouseEvent<HTMLButtonElement>): void;
    closeModal(event?: React.MouseEvent<HTMLButtonElement>): void;
}

interface IState {
    submitting: boolean;
}

class Modal extends React.Component<IProps, IState> {
    modal: any;
    elem: any;
    constructor(props: any) {
        super(props);
        this.onSubmit = this.onSubmit.bind(this);
        this.state = {submitting: false};
        this.modal = null;
    }

    componentDidMount() {
        const options: any = {};

        if (this.props.clickOutsideToClose !== true) {
            options.backdrop = 'static';
        }

        if (this.elem) {
            this.modal = new BSModal(this.elem);
            this.modal.show();
            this.elem.addEventListener('hidden.bs.modal', () => {
                this.props.closeModal();
            });
        }
    }

    componentWillUnmount() {
        if (this.elem && this.modal) {
            this.modal.hide();
        }
    }

    onSubmit(e: any) {
        if (this.props.disableButtonOnSubmit) {
            this.setState({submitting: true});
            this.props.onSubmit(e);
            return;
        }

        this.props.onSubmit(e);
    }

    render() {
        return (
            <div className={classNames('modal', {
                'modal--full-width': this.props.width === 'full',
                'mt-xl-5': this.props.width !== 'full',
                [this.props.className ?? '']: this.props.className != null,
            })}
            ref={(elem: any) => this.elem = elem} role={gettext('dialog')} aria-label={this.props.title}>
                <h3 className="a11y-only">{this.props.title}</h3>
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h5 className="modal-title">{this.props.title}</h5>
                            <CloseButton onClick={this.props.closeModal} />
                        </div>
                        <div className="modal-body">
                            {this.props.children}
                        </div>
                        <div className="modal-footer">
                            <ModalSecondaryButton
                                type="reset"
                                label={this.props.onCancelLabel || gettext('Cancel')}
                                onClick={this.props.closeModal}
                            />
                            {' '}
                            <ModalPrimaryButton
                                type="submit"
                                label={this.props.onSubmitLabel || gettext('Save')}
                                onClick={this.onSubmit}
                                disabled={this.state.submitting || !this.props.formValid}
                            />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state: any) => ({formValid: get(state, 'modal.formValid') === true});
const mapDispatchToProps = (dispatch: any) => ({closeModal: () => dispatch(closeModal())});

const component: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(Modal);

export default component;
