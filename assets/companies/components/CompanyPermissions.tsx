import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';

import CheckboxInput from 'components/CheckboxInput';

function CompanyPermissions({
    sections,
    products,
    permissions,
    save,
    toggleGeneralPermission,
    toggleProductPermission,
    updateProductSeats,
}) {
    return (
        <div className='tab-pane active' id='company-permissions'>
            <form onSubmit={save}>
                <div className="list-item__preview-form" key='general'>
                    <div className="form-group">
                        <label>{gettext('General')}</label>
                        <ul className="list-unstyled">
                            <li>
                                <CheckboxInput
                                    name="archive_access"
                                    label={gettext('Grant Access To Archived Wire')}
                                    value={!!permissions.archive_access}
                                    onChange={() => {
                                        toggleGeneralPermission('archive_access');
                                    }}
                                />
                            </li>
                            <li>
                                <CheckboxInput
                                    name="events_only"
                                    label={gettext('Events Only Access')}
                                    value={!!permissions.events_only}
                                    onChange={() => {
                                        toggleGeneralPermission('events_only');
                                    }}
                                />
                                <CheckboxInput
                                    name="restrict_coverage_info"
                                    label={gettext('Restrict Coverage Info')}
                                    value={!!permissions.restrict_coverage_info}
                                    onChange={() => {
                                        toggleGeneralPermission('restrict_coverage_info');
                                    }}
                                />
                            </li>
                        </ul>
                    </div>

                    <div className="form-group" key='sections'>
                        <label>{gettext('Sections')}</label>
                        <ul className="list-unstyled">
                            {sections.map((item) => (
                                <li key={item._id}>
                                    <CheckboxInput
                                        name={item._id}
                                        label={item.name}
                                        value={!!permissions.sections[item._id]}
                                        onChange={() => {
                                            toggleProductPermission('sections', item._id);
                                        }}
                                    />
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="form-group" key='products'>
                        {sections.map((section) => (
                            [<label key={`${section.id}label`}>{gettext('Products')} {`(${section.name})`}</label>,
                                <ul key={`${section.id}product`} className="list-unstyled">
                                    {products.filter((p) => (p.product_type || 'wire').toLowerCase() === section._id.toLowerCase())
                                        .map((product) => (
                                            <li key={product._id}>
                                                <div className="input-group">
                                                    <div className="input-group-text border-0 bg-transparent">
                                                        <CheckboxInput
                                                            name={product._id}
                                                            label={product.name}
                                                            value={!!permissions.products[product._id]}
                                                            onChange={() => {
                                                                toggleProductPermission('products', product._id);
                                                            }}
                                                        />
                                                    </div>
                                                    {!permissions.products[product._id] ? null : (
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
                                                                style={{maxWidth: '100px'}}
                                                                min="0"
                                                                tabIndex="0"
                                                                value={(permissions.seats[product._id] || 0).toString()}
                                                                onChange={(event) => {
                                                                    updateProductSeats(product._id, event.target.value);
                                                                }}
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

CompanyPermissions.propTypes = {
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
    toggleGeneralPermission: PropTypes.func.isRequired,
    toggleProductPermission: PropTypes.func.isRequired,
    updateProductSeats: PropTypes.func.isRequired,
};

export default CompanyPermissions;
