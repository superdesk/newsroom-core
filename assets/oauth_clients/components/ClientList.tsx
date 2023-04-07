import React from 'react';
import PropTypes from 'prop-types';
import ClientListItem from './ClientListItem';
import {gettext} from 'utils';


function ClientList({clients, onClick}) {
    const list = clients.map((client) =>
        <ClientListItem
            key={client._id}
            client={client}
            onClick={onClick}
        />
    );

    return (
        <section className="content-main">
            <div className="list-items-container">
                <table className="table table-hover">
                    <thead>
                        <tr>
                            <th>{ gettext('Name') }</th>
                            <th>{ gettext('Created On') }</th>
                            <th>{ gettext('Last Login') }</th>
                        </tr>
                    </thead>
                    <tbody>{list}</tbody>
                </table>
            </div>
        </section>
    );
}

ClientList.propTypes = {
    clients: PropTypes.array.isRequired,
    onClick: PropTypes.func.isRequired,
};

export default ClientList;
