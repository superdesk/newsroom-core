import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {gettext} from 'utils';
import {get} from 'lodash';

import CheckboxInput from 'components/CheckboxInput';
import TextInput from 'components/TextInput';

import {savePermissions} from '../actions';

class CompanyPermissions extends React.Component {

    constructor(props) {
        super(props);
        this.state = this.setup();
    }

    setup() {
        const products = {};
        const seats = {};
        const companyProductsById = (get(this.props, 'company.products')|| []).reduce((productMap, product) => {
            productMap[product._id] = product;

            return productMap;
        }, {});

        this.props.products.forEach((product) => {
            if (companyProductsById[product._id] != null) {
                products[product._id] = true;
                seats[product._id] = companyProductsById[product._id].seats || 0;
            } else {
                products[product._id] = false;
                seats[product._id] = 0;
            }
        });

        const sections = {};

        if (this.props.company.sections) {
            Object.assign(sections, this.props.company.sections);
        } else {
            this.props.sections.forEach((section) => {
                sections[section._id] = false;
            });
        }

        const archive_access = !!this.props.company.archive_access;
        const events_only = !!this.props.company.events_only;
        const restrict_coverage_info = !!this.props.company.restrict_coverage_info;

        return {sections, products, archive_access, events_only, restrict_coverage_info, seats};
    }

    componentDidUpdate(prevProps) {
        if (prevProps.company !== this.props.company) {
            this.setState(this.setup());
        }
    }

    toggle(key, _id) {
        const field = this.state[key];
        field[_id] = !field[_id];
        this.setState({[key]: field});
    }

    setSeats(productId, seats) {
        this.setState((prevState) => ({
            seats: {
                ...prevState.seats,
                [productId]: parseInt(seats),
            },
        }));
    }

    render() {
        return (
            <div className='tab-pane active' id='company-permissions'>
                <form onSubmit={(event) => {
                    event.preventDefault();
                    this.props.savePermissions(this.props.company, this.state);
                }}>
                    <div className="list-item__preview-form" key='general'>
                        <div className="form-group">
                            <label>{gettext('General')}</label>
                            <ul className="list-unstyled">
                                <li>
                                    <CheckboxInput
                                        name="archive_access"
                                        label={gettext('Grant Access To Archived Wire')}
                                        value={!!this.state.archive_access}
                                        onChange={() => this.setState({archive_access: !this.state.archive_access})}
                                    />
                                </li>
                                <li>
                                    <CheckboxInput
                                        name="events_only"
                                        label={gettext('Events Only Access')}
                                        value={!!this.state.events_only}
                                        onChange={() => this.setState({events_only: !this.state.events_only})}
                                    />
                                    <CheckboxInput
                                        name="restrict_coverage_info"
                                        label={gettext('Restrict Coverage Info')}
                                        value={!!this.state.restrict_coverage_info}
                                        onChange={() => this.setState({restrict_coverage_info: !this.state.restrict_coverage_info})}
                                    />
                                </li>
                            </ul>
                        </div>

                        <div className="form-group" key='sections'>
                            <label>{gettext('Sections')}</label>
                            <ul className="list-unstyled">
                                {this.props['sections'].map((item) => (
                                    <li key={item._id}>
                                        <CheckboxInput
                                            name={item._id}
                                            label={item.name}
                                            value={!!this.state['sections'][item._id]}
                                            onChange={() => this.toggle('sections', item._id)} />
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className="form-group" key='products'>
                            {this.props['sections'].map((section) => (
                                [<label key={`${section.id}label`}>{gettext('Products')} {`(${section.name})`}</label>,
                                    <ul key={`${section.id}product`} className="list-unstyled">
                                        {this.props['products'].filter((p) => (p.product_type || 'wire').toLowerCase() === section._id.toLowerCase())
                                            .map((product) => (
                                                <li key={product._id}>
                                                    <div className="input-group">
                                                        <div className="input-group-text border-0 bg-transparent">
                                                            <CheckboxInput
                                                                name={product._id}
                                                                label={product.name}
                                                                value={!!this.state.products[product._id]}
                                                                onChange={() => this.toggle('products', product._id)}
                                                            />
                                                        </div>
                                                        {!this.state['products'][product._id] ? null : (
                                                            <React.Fragment>
                                                                <label
                                                                    className="input-group-text border-0 bg-transparent ms-auto"
                                                                    htmlFor={`${product._id}_seats`}
                                                                >
                                                                    {gettext('Seats:')}
                                                                </label>
                                                                <input
                                                                    type="number"
                                                                    id={`${product._id}_seats`}
                                                                    name={`${product._id}_seats`}
                                                                    className="form-control"
                                                                    style={{maxWidth: "100px"}}
                                                                    min="0"
                                                                    tabIndex="0"
                                                                    value={(this.state.seats[product._id] || 0).toString()}
                                                                    onChange={(event) => this.setSeats(product._id, event.target.value)}
                                                                />
                                                            </React.Fragment>
                                                        )}
                                                    </div>
                                                </li>
                                            ))}
                                    </ul>]
                            ))}
                        </div>

                    </div>
                    <div className='list-item__preview-footer'>
                        <input
                            type='submit'
                            className='btn btn-outline-primary'
                            value={gettext('Save')}
                        />
                    </div>
                </form>
            </div>
        );
    }
}

CompanyPermissions.propTypes = {
    company: PropTypes.shape({
        _id: PropTypes.string.isRequired,
        sections: PropTypes.object,
        archive_access: PropTypes.bool,
        events_only: PropTypes.bool,
        restrict_coverage_info: PropTypes.bool,
    }).isRequired,

    sections: PropTypes.arrayOf(PropTypes.shape({
        _id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
    })),
    products: PropTypes.arrayOf(PropTypes.object).isRequired,

    savePermissions: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
    sections: state.sections,
    products: state.products,
});

const mapDispatchToProps = {
    savePermissions,
};

export default connect(mapStateToProps, mapDispatchToProps)(CompanyPermissions);
