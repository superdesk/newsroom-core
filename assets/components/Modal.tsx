import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {connect} from 'react-redux';
import {Modal as BSModal} from 'bootstrap';

import {gettext} from 'utils';
import {closeModal} from 'actions';

import CloseButton from './CloseButton';
import classNames from 'classnames';

/**
 * Primary modal button for actions like save/send/etc
 *
 * @param {string} label
 * @param {string} type
 * @param {func} onClick
 */
export function ModalPrimaryButton({label, type, onClick, disabled}: any) {
    assertButtonHandler(label, type, onClick);
    return (
        <button type={type || 'button'}
            onClick={onClick}
            className="nh-button nh-button--primary"
            disabled={disabled}
        >{label}</button>
    );
}

ModalPrimaryButton.propTypes = {
    label: PropTypes.string.isRequired,
    type: PropTypes.string,
    onClick: PropTypes.func,
    disabled: PropTypes.bool,
};

/**
 * Secondary modal button for actions like cancel/reset
 *
 * @param {string} label
 * @param {string} type
 * @param {func} onClick
 */
export function ModalSecondaryButton({label, type, onClick}: any) {
    assertButtonHandler(label, type, onClick);
    return (
        <button type={type || 'button'}
            onClick={onClick}
            className="nh-button nh-button--secondary"
        >{label}</button>
    );
}

ModalSecondaryButton.propTypes = {
    'label': PropTypes.string.isRequired,
    onClick: PropTypes.func,
    type: PropTypes.string,
};

/**
 * Test if button makes any sense
 *
 * either type or onClick handler must be specified
 *
 * @param {string} label
 * @param {string} type
 * @param {func} onClick
 */
function assertButtonHandler(label: any, type: any, onClick: any) {
    if (!type && !onClick) {
        console.warn('You should use either type or onClick handler for button', label);
    }
}

class Modal extends React.Component<any, any> {
    static propTypes: any;
    static defaultProps: any;

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

        if (!this.props.clickOutsideToClose) {
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
            <div className={classNames('modal mt-xl-5', {
                'modal--full-width': this.props.width === 'full',
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
                                label={this.props.onCancelLabel}
                                onClick={this.props.closeModal}
                            />
                            {' '}
                            <ModalPrimaryButton
                                type="submit"
                                label={this.props.onSubmitLabel}
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

Modal.propTypes = {
    title: PropTypes.string.isRequired,
    children: PropTypes.node.isRequired,
    onSubmit: PropTypes.func,
    onSubmitLabel: PropTypes.string,
    onCancelLabel: PropTypes.string,
    closeModal: PropTypes.func.isRequired,
    disableButtonOnSubmit: PropTypes.bool,
    formValid: PropTypes.bool,
    clickOutsideToClose: PropTypes.bool,
    width: PropTypes.string,
};

Modal.defaultProps = {
    onSubmitLabel: gettext('Save'),
    onCancelLabel: gettext('Cancel'),
    clickOutsideToClose: false,
};

const mapStateToProps = (state: any) => ({formValid: get(state, 'modal.formValid')});

const component: React.ComponentType<any> = connect(mapStateToProps, {closeModal})(Modal);

export default component;
