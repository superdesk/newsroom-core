import * as React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {sendProductSeatRequest} from '../actions';
import {closeModal, modalFormValid, modalFormInvalid} from 'actions';
import {gettext} from 'utils';
import {currentCompanySectionListSelector, productListSelector} from '../selectors';

import Modal from 'components/Modal';
import TextInput from 'components/TextInput';
import TextAreaInput from 'components/TextAreaInput';
import {Tag} from 'components/Tag';

class CompanyAdminProductSeatRequestModalComponent extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            productIds: this.props.productIds || [],
            numberOfSeats: 30,
            note: '',
        };
        this.submit = this.submit.bind(this);
        this.updateNumberOfSeats = this.updateNumberOfSeats.bind(this);
        this.updateNote = this.updateNote.bind(this);
        this.validateForm = this.validateForm.bind(this);
    }

    componentDidMount() {
        this.validateForm();
    }

    submit() {
        this.props.sendRequest({
            product_ids: this.state.productIds,
            number_of_seats: this.state.numberOfSeats,
            note: this.state.note,
        }).then(() => {
            this.props.closeModal();
        });
    }

    toggleProduct(productId) {
        let productIds = Array.from(this.state.productIds);

        if (productIds.includes(productId)) {
            productIds = productIds.filter((pId) => pId !== productId);
        } else {
            productIds.push(productId);
        }

        this.setState({productIds: productIds}, this.validateForm);
    }

    updateNumberOfSeats(event) {
        this.setState({numberOfSeats: parseInt(event.target.value, 10)}, this.validateForm);
    }

    updateNote(event) {
        this.setState({note: event.target.value});
    }

    getProductGroups() {
        const products = [];

        this.props.sections.forEach((section) => {
            products.push({
                _id: section._id,
                name: section.name,
                products: this.props.products.filter(
                    (product) => (product.product_type === section._id)
                ),
            });
        });

        return products;
    }

    validateForm() {
        if (!(this.state.productIds || []).length || this.state.numberOfSeats <= 0) {
            this.props.modalFormInvalid();
        } else {
            this.props.modalFormValid();
        }
    }

    render() {
        const sectionProducts = this.getProductGroups();
        const selectedProducts = this.state.productIds.map((productId) => (
            this.props.products.find((product) => product._id === productId)
        ));

        return (
            <Modal
                title={gettext('Request more seats')}
                onSubmitLabel={gettext('Send Request')}
                disableButtonOnSubmit={true}
                onSubmit={this.submit}
                closeModal={this.props.closeModal}
                clickOutsideToClose={true}
            >
                <form onSubmit={(event) => {event.preventDefault();}}>
                    <div className="tags-list mb-3">
                        <button
                            className="icon-button icon-button--primary icon-button--small icon-button--bordered"
                            type="button"
                            data-bs-toggle="dropdown"
                            aria-haspopup='true'
                            aria-expanded="false"
                            aria-label="Add Product"
                        >
                            <i className="icon--plus"></i>
                        </button>
                        <ul className="dropdown-menu">
                            {sectionProducts.map((section, index) => (
                                <React.Fragment key={section._id}>
                                    <h6 className="dropdown-header">
                                        {section.name}
                                    </h6>
                                    <div className="dropdown-divider" />
                                    {section.products.map((product) => (
                                        <li key={product._id}>
                                            <button
                                                className="dropdown-item"
                                                onClick={() => this.toggleProduct(product._id)}
                                                disabled={this.state.productIds.includes(product._id)}
                                            >
                                                {product.name}
                                            </button>
                                        </li>
                                    ))}
                                    {index >= (sectionProducts.length - 1) ? null : (
                                        <div className="dropdown-divider" />
                                    )}
                                </React.Fragment>
                            ))}
                        </ul>
                        {selectedProducts.map((product) => (
                            <Tag
                                key={product._id}
                                label={product.product_type === 'wire' ? gettext('Wire') : gettext('Agenda')}
                                text={product.name}
                                keyValue={product._id}
                                onClick={() => this.toggleProduct(product._id)}
                                shade="light"
                            />
                        ))}
                    </div>
                    <TextInput
                        type="number"
                        label={gettext('Number of additional seats')}
                        name="numberOfSeats"
                        value={(this.state.numberOfSeats || 0).toString()}
                        required={true}
                        min={1}
                        onChange={this.updateNumberOfSeats}
                    />
                    <TextAreaInput
                        name="note"
                        label={gettext('Note')}
                        value={this.state.note}
                        onChange={this.updateNote}
                        rows={5}
                    />
                </form>
            </Modal>
        );
    }
}

CompanyAdminProductSeatRequestModalComponent.propTypes = {
    productIds: PropTypes.arrayOf(PropTypes.string),
    products: PropTypes.arrayOf(PropTypes.object),
    closeModal: PropTypes.func,
    sendRequest: PropTypes.func,
    sections: PropTypes.arrayOf(PropTypes.shape({
        _id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
    })),
    modalFormInvalid: PropTypes.func,
    modalFormValid: PropTypes.func,
};

const mapStateToProps = (state) => ({
    products: productListSelector(state),
    productIds: get(state, 'modal.data.productIds') || [],
    sections: currentCompanySectionListSelector(state),
});

const mapDispatchToProps = (dispatch) => ({
    closeModal: () => dispatch(closeModal()),
    sendRequest: (data) => dispatch(sendProductSeatRequest(data)),
    modalFormInvalid: () => dispatch(modalFormInvalid()),
    modalFormValid: () => dispatch(modalFormValid()),
});

export const CompanyAdminProductSeatRequestModal = connect(
    mapStateToProps,
    mapDispatchToProps
)(CompanyAdminProductSeatRequestModalComponent);
