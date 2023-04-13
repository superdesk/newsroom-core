import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import ListBar from 'assets/components/ListBar';
import {setSearchQuery} from 'assets/search/actions';
import {gettext} from 'assets/utils';
import {newClient, fetchClients} from '../actions';
import Clients from './Clients';

class ClientsApp extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any, context: any) {
        super(props, context);
    }

    render() {
        return (
            [<ListBar
                key="ClientBar"
                onNewItem={this.props.newClient}
                setQuery={this.props.setQuery}
                fetch={this.props.fetchClients}
                buttonText={gettext('New Client')}
            />,
            <Clients key="Clients" />
            ]
        );
    }
}

ClientsApp.propTypes = {
    clients: PropTypes.arrayOf(PropTypes.object),
    clientToEdit: PropTypes.object,
    selectClient: PropTypes.func,
    editClient: PropTypes.func,
    saveClient: PropTypes.func,
    deleteClient: PropTypes.func,
    newClient: PropTypes.func,
    cancelEdit: PropTypes.func,
    isLoading: PropTypes.bool,
    activeQuery: PropTypes.string,
    totalClients: PropTypes.number,
    clientsById: PropTypes.object,
    fetchClients: PropTypes.func,
    setQuery: PropTypes.func,
    errors: PropTypes.object,
    dispatch: PropTypes.func,
};


const mapDispatchToProps = {
    newClient,
    fetchClients,
    setQuery: setSearchQuery,
};

export default connect(null, mapDispatchToProps)(ClientsApp);

