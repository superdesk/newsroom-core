import React from 'react';
import PropTypes from 'prop-types';
import {gettext, shortDate, onActivationKey} from 'utils';


function ProductListItem({product, isActive, onClick}: any) {
    return (
        <tr key={product._id}
            className={isActive ? 'table--selected' : undefined}
            onClick={() => onClick(product._id)}
            onKeyDown={onActivationKey(() => onClick(product._id))}
            tabIndex={0}>
            <td className="name">{product.name}</td>
            <td>{(product.is_enabled ? gettext('Enabled') : gettext('Disabled'))}</td>
            <td>{gettext(product.sd_product_id)}</td>
            <td>{gettext(product.query)}</td>
            {product.product_type === 'agenda' && <td>{gettext(product.planning_item_query)}</td>}
            <td>{shortDate(product._created)}</td>
        </tr>
    );
}

ProductListItem.propTypes = {
    product: PropTypes.object,
    isActive: PropTypes.bool,
    onClick: PropTypes.func,
};

export default ProductListItem;