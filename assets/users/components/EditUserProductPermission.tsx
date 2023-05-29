import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {isProductEnabled} from 'companies/utils';
import CheckboxInput from 'components/CheckboxInput';

export function EditUserProductPermission({original, user, section, product, seats, onChange}) {
    const originallyEnabled = isProductEnabled(original.products || [], product._id);
    const currentlyEnabled = isProductEnabled(user.products || [], product._id);
    const maxSeats = seats[user.company][product._id].max_seats;
    let assignedSeats = seats[user.company][product._id].assigned_seats;

    // Update the count/max reached for this form only, to reflect any current changes
    if (originallyEnabled !== currentlyEnabled) {
        if (currentlyEnabled) {
            assignedSeats += 1;
        } else {
            assignedSeats -= 1;
        }
    }
    const maxReached = assignedSeats >= maxSeats;

    return (
        <div className="list-item__preview-row">
            <div className="form-group">
                <CheckboxInput
                    name={`products.${section._id}.${product._id}`}
                    label={product.name}
                    value={currentlyEnabled}
                    onChange={onChange}
                    readOnly={currentlyEnabled === false && maxReached === true}
                />
            </div>
            <div className={classNames({'text-danger': maxReached === true})}>
                {assignedSeats}/{maxSeats}
            </div>
        </div>
    );
}

EditUserProductPermission.propTypes = {
    original: PropTypes.object,
    user: PropTypes.object.isRequired,
    section: PropTypes.object.isRequired,
    product: PropTypes.object.isRequired,
    seats: PropTypes.object,
    onChange: PropTypes.func,
};
