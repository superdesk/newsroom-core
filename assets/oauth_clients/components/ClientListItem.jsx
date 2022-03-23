import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {shortDate} from 'utils';

function ClientListItem({client, onClick}) {
    return (
        <tr key={client._id}
            className={classNames({'table-secondary': false})}
            onClick={() => onClick(client._id)}
        >
            <td className="name">{client.name}</td>
            <td>{shortDate(client._created)}</td>
            {(!client.last_active) ? (<td></td>) : (
                <td>{shortDate(client.last_active)}</td>
            )}
        </tr>
    );
}

ClientListItem.propTypes = {
    client: PropTypes.object,
    onClick: PropTypes.func,
};

export default ClientListItem;
