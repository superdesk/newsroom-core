import * as React from 'react';
import PropTypes from 'prop-types';

import {gettext} from 'utils';
import {getConfig} from 'utils';

export function CompanyDetailsProductRow({seat, onNameClicked, showSeatRequestModal}) {
    return (
        <tr>
            <td
                onClick={onNameClicked}
                className={!seat.max_reached ? undefined : 'text-danger'}
            >
                {seat.name}
            </td>
            {getConfig('allow_companies_to_manage_products') && (
                <td className={!seat.max_reached ? undefined : 'text-danger'}>
                    {seat.assigned_seats}/{seat.max_seats}
                </td>
            )}
            <td className="font-light">{seat.description}</td>
            {getConfig('allow_companies_to_manage_products') && (
                <td>
                    <button
                        className="btn btn-sm btn-outline-light"
                        onClick={() => showSeatRequestModal([seat._id])}
                    >
                        {gettext('Request more seats')}
                    </button>
                </td>
            )}
        </tr>
    );
}

CompanyDetailsProductRow.propTypes = {
    seat: PropTypes.shape({
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
