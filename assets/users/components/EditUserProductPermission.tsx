import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {isProductEnabled} from 'companies/utils';
import CheckboxInput from 'components/CheckboxInput';
import {hasSeatsAvailable, hasUnlimitedSeats} from 'users/utils';

export function EditUserProductPermission({original, user, section, product, seats, onChange}: any): any {
    const maxSeats = user.company != null ?
        seats[user.company][product._id].max_seats :
        null;
    let assignedSeats = user.company != null ?
        seats[user.company][product._id].assigned_seats :
        null;

    const originallyEnabled = isProductEnabled(original.products || [], product._id);
    const currentlyEnabled = isProductEnabled(user.products || [], product._id);

    const unlimited = hasUnlimitedSeats(user.company, seats, product);

    // Update the count/max reached for this form only, to reflect any current changes
    if (maxSeats != null && originallyEnabled !== currentlyEnabled) {
        if (currentlyEnabled) {
            assignedSeats += 1;
        } else {
            assignedSeats -= 1;
        }
    }
    const maxReached = maxSeats && assignedSeats >= maxSeats;
    const canToggleSeatSelection = hasSeatsAvailable(user.company, seats, product) || currentlyEnabled;

    return (
        <div className="list-item__preview-row">
            <div className="form-group">
                <CheckboxInput
                    name={`products.${section._id}.${product._id}`}
                    label={product.name}
                    value={currentlyEnabled || unlimited}
                    onChange={onChange}
                    readOnly={canToggleSeatSelection !== true}
                />
            </div>
            {unlimited ? null : (
                <div className={classNames({'text-danger': maxReached === true})}>
                    {assignedSeats}/{maxSeats}
                </div>
            )}
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
