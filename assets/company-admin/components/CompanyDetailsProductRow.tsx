import * as React from 'react';
import PropTypes from 'prop-types';

import {gettext, getConfig} from 'utils';
import classNames from 'classnames';

export function CompanyDetailsProductRow({product, onNameClicked, showSeatRequestModal}: any) {
    const unlimited = product.max_seats == null || product.max_seats < 1;
    const textClassName = classNames({
        'text-danger': product.max_reached,
        'text-secondary': unlimited,
    });

    return (
        <tr>
            <td
                onClick={onNameClicked}
                className={textClassName}
            >
                {product.name}
            </td>
            {getConfig('allow_companies_to_manage_products') && (
                <td className={textClassName}>
                    {unlimited ? (
                        gettext('Unlimited')
                    ) : (
                        `${product.assigned_seats}/${product.max_seats}`
                    )}
                </td>
            )}
            <td className="font-light">{product.description}</td>
            {getConfig('allow_companies_to_manage_products') && !unlimited && (
                <td>
                    <button
                        className="nh-button nh-button--tertiary nh-button--small"
                        onClick={() => showSeatRequestModal([product._id])}
                    >
                        {gettext('Request more seats')}
                    </button>
                </td>
            )}
        </tr>
    );
}

CompanyDetailsProductRow.propTypes = {
    product: PropTypes.shape({
        _id: PropTypes.string,
        name: PropTypes.string,
        description: PropTypes.string,
        section: PropTypes.string,
        max_seats: PropTypes.number,
        assigned_seats: PropTypes.number,
        max_reached: PropTypes.bool,
    }),
    onNameClicked: PropTypes.func,
    showSeatRequestModal: PropTypes.func,
};
