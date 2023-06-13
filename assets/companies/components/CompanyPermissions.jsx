import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';

import CheckboxInput from 'components/CheckboxInput';

function CompanyPermissions({
    company,
    sections,
    products,
    save,
    onChange,
    toggleCompanySection,
    toggleCompanyProduct,
    updateCompanySeats,
}) {
    const productsEnabled = (company.products || []).map((product) => product._id);
    const seats = (company.products || []).reduce((productSeats, product) => {
        productSeats[product._id] = product.seats;

        return productSeats;
    }, {});

    return (
        <div className='tab-pane active' id='company-permissions'>
            <form onSubmit={save}>
                <div className="list-item__preview-form" key='general'>
                    <div
                        data-test-id="group--general"
                        className="form-group"
                    >
                        <div className="list-item__preview-collapsible list-item__preview-collapsible--read-only list-item__preview-collapsible--small mb-2">
                            <div className="list-item__preview-collapsible-header">
                                <i className="icon--arrow-right icon--rotate-90"></i>
                                <h3>{gettext('General')}</h3>
                            </div>
                        </div>
                        <ul className="list-unstyled">
                            <li className="item--min-height-40">
                                <CheckboxInput
                                    name="archive_access"
                                    label={gettext('Grant Access To Archived Wire')}
                                    value={company.archive_access === true}
                                    onChange={onChange}
                                />
                            </li>
                            <li className="item--min-height-40">
                                <CheckboxInput
                                    name="events_only"
                                    label={gettext('Events Only Access')}
                                    value={company.events_only === true}
                                    onChange={onChange}
                                />
                            </li>
                            <li className="item--min-height-40">
                                <CheckboxInput
                                    name="restrict_coverage_info"
                                    label={gettext('Restrict Coverage Info')}
                                    value={company.restrict_coverage_info === true}
                                    onChange={onChange}
                                />
                            </li>
                        </ul>
                    </div>

                    <div
                        data-test-id="group--sections"
                        className="form-group"
                        key="sections"
                    >
                        <div className="list-item__preview-collapsible list-item__preview-collapsible--read-only list-item__preview-collapsible--small mb-2">
                            <div className="list-item__preview-collapsible-header">
                                <i className="icon--arrow-right icon--rotate-90"></i>
                                <h3>{gettext('Sections')}</h3>
                            </div>
                        </div>
                        <ul className="list-unstyled">
                            {sections.map((item) => (
                                <li className="item--min-height-40" key={item._id}>
                                    <CheckboxInput
                                        name={item._id}
                                        label={item.name}
                                        value={(company.sections || {})[item._id] === true}
                                        onChange={toggleCompanySection.bind(null, item._id)}
                                    />
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div
                        data-test-id="group--products"
                        className="form-group"
                        key="products"
                    >
                        {sections.filter((section) => (company.sections || {})[section._id] === true).map((section) => (
                            [<div key={`${section.id}product`} className="list-item__preview-collapsible list-item__preview-collapsible--read-only list-item__preview-collapsible--small mb-2">
                                <div className="list-item__preview-collapsible-header">
                                    <i className="icon--arrow-right icon--rotate-90"></i>
                                    <h3 key={`${section.id}label`}>{gettext('Products')} {`(${section.name})`}</h3>
                                </div>
                            </div>,

                            <div key={`${section.id}product`} className="products-list__heading d-flex justify-content-between align-items-center">
                                <span className="item--left">{gettext('Product')}</span>
                                <span className="item--right">{gettext('Number of seats')}</span>
                            </div>,
                            <ul key={`${section.id}product`} className="list-unstyled">
                                {products.filter((p) => (p.product_type || 'wire').toLowerCase() === section._id.toLowerCase())
                                    .map((product) => (
                                        <li key={product._id}>
                                            <div className="products-list__product">
                                                <div className="products-list__product-select">
                                                    <CheckboxInput
                                                        name={product._id}
                                                        label={product.name}
                                                        value={productsEnabled.includes(product._id)}
                                                        onChange={() => {
                                                            toggleCompanyProduct(
                                                                product._id,
                                                                section._id,
                                                                !productsEnabled.includes(product._id)
                                                            );
                                                        }}
                                                    />
                                                </div>
                                                {!productsEnabled.includes(product._id) ? null : (
                                                    <div className="products-list__value">
                                                        <label
                                                            className="a11y-only"
                                                            htmlFor={`${product._id}_seats`}
                                                        >
                                                            {gettext('Seats:')}
                                                        </label>
                                                        <input
                                                            data-test-id={`field-${product._id}_seats`}
                                                            type="number"
                                                            id={`${product._id}_seats`}
                                                            name={`${product._id}_seats`}
                                                            className="form-control form-control--small form-control--right form-control--compact"
                                                            style={{maxWidth: '60px'}}
                                                            min="0"
                                                            tabIndex="0"
                                                            value={(seats[product._id] || 0).toString()}
                                                            onChange={(event) => {
                                                                updateCompanySeats(
                                                                    product._id,
                                                                    parseInt(event.target.value)
                                                                );
                                                            }}
                                                        />
                                                    </div>
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
                        data-test-id="save-btn"
                        type='submit'
                        className='nh-button nh-button--primary'
                        value={gettext('Save')}
                    />
                </div>
            </form>
        </div>
    );
}

CompanyPermissions.propTypes = {
    company: PropTypes.object,
    sections: PropTypes.arrayOf(PropTypes.shape({
        _id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
    })),
    products: PropTypes.arrayOf(PropTypes.shape({
        _id: PropTypes.string,
        name: PropTypes.string,
        product_type: PropTypes.string,
    })).isRequired,
    permissions: PropTypes.shape({
        archive_access: PropTypes.bool,
        events_only: PropTypes.bool,
        restrict_coverage_info: PropTypes.bool,
        sections: PropTypes.object,
        products: PropTypes.object,
        seats: PropTypes.object,
    }),

    save: PropTypes.func.isRequired,
    onChange: PropTypes.func.isRequired,
    toggleCompanySection: PropTypes.func.isRequired,
    toggleCompanyProduct: PropTypes.func.isRequired,
    updateCompanySeats: PropTypes.func.isRequired,
};

export default CompanyPermissions;
