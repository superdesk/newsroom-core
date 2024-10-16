import React from 'react';
import {get} from 'lodash';
import {connect} from 'react-redux';
import {Modal as BSModal} from 'bootstrap';
import {gettext} from 'utils';
import {closeModal} from 'actions';
import CloseModalButton from './CloseModalButton';
import classNames from 'classnames';
import {Button} from 'components/Buttons';

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
    footer?(): React.ComponentType | React.JSX.Element;
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
            <div
                className={classNames('modal', {
                    'modal--full-width': this.props.width === 'full',
                    'mt-xl-5': this.props.width !== 'full',
                    [this.props.className ?? '']: this.props.className != null,
                })}
                ref={(elem: HTMLDivElement) => this.elem = elem}
                role="dialog"
                aria-label={this.props.title}
            >
                <h3 className="a11y-only">{this.props.title}</h3>
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h5 className="modal-title">{this.props.title}</h5>
                            <CloseModalButton onClick={this.props.closeModal} />
                        </div>
                        <div className="modal-body">
                            {this.props.children}
                        </div>\
                        {this.props.footer != null ? this.props.footer() : (
                            <div className="modal-footer">
                                <Button
                                    type='reset'
                                    variant='secondary'
                                    value={this.props.onCancelLabel || gettext('Cancel')}
                                    onClick={this.props.closeModal}
                                />
                                <Button
                                    type='submit'
                                    variant='primary'
                                    value={this.props.onSubmitLabel || gettext('Save')}
                                    disabled={this.state.submitting || !this.props.formValid}
                                    onClick={this.onSubmit}
                                />     
                            </div>
                        )}
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
