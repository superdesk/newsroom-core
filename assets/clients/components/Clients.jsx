import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import EditClient from './EditClient';
import ClientList from './ClientList';
import SearchResults from 'search/components/SearchResults';

import {
    cancelEdit,
    deleteClient,
    editClient,
    postClient,
    selectClient,
    setError,
} from '../actions';
import {searchQuerySelector} from 'search/selectors';
import {gettext} from 'utils';

class Clients extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.isFormValid = this.isFormValid.bind(this);
        this.save = this.save.bind(this);
        this.deleteClient = this.deleteClient.bind(this);
    }

    isFormValid() {
        let valid = true;
        let errors = {};

        if (!this.props.clientToEdit.name) {
            errors.name = [gettext('Please provide client name')];
            valid = false;
        }

        this.props.dispatch(setError(errors));
        return valid;
    }

    save(externalEvent) {
        if (externalEvent) {
            externalEvent.preventDefault();

            if (!this.isFormValid()) {
                return;
            }
        }

        this.props.saveClient('clients');
    }

    deleteClient(event) {
        event.preventDefault();

        if (confirm(gettext('Would you like to delete client: {{name}}', {name: this.props.clientToEdit.name}))) {
            this.props.deleteClient('clients');
        }
    }

    render() {
        const progressStyle = {width: '25%'};
        const originalClientEdited = !get(this.props, 'clientToEdit._id') ? this.props.clientToEdit :
            this.props.clientsById[this.props.clientToEdit._id];
        return (
            <div className="flex-row">
                {(this.props.isLoading ?
                    <div className="col d">
                        <div className="progress">
                            <div className="progress-bar" style={progressStyle} />
                        </div>
                    </div>
                    :
                    <div className="flex-col flex-column">
                        {this.props.activeQuery && (
                            <SearchResults
                                showTotalItems={true}
                                showTotalLabel={true}
                                showSaveTopic={false}
                                totalItems={this.props.totalClients}
                                totalItemsLabel={this.props.activeQuery}
                            />
                        )}
                        <ClientList
                            clients={this.props.clients}
                            onClick={this.props.selectClient}
                        />
                    </div>
                )}
                {this.props.clientToEdit &&
                    <EditClient
                        originalItem={originalClientEdited}
                        client={this.props.clientToEdit}
                        onChange={this.props.editClient}
                        onSave={this.save}
                        onClose={this.props.cancelEdit}
                        onDelete={this.deleteClient}
                    />
                }
            </div>
        );
    }
}

Clients.propTypes = {
    clients: PropTypes.arrayOf(PropTypes.object),
    clientToEdit: PropTypes.object,
    activeClientId: PropTypes.string,
    selectClient: PropTypes.func,
    editClient: PropTypes.func,
    saveClient: PropTypes.func,
    deleteClient: PropTypes.func,
    newClient: PropTypes.func,
    cancelEdit: PropTypes.func,
    isLoading: PropTypes.bool,
    activeQuery: PropTypes.string,
    totalClients: PropTypes.number,
    errors: PropTypes.object,
    dispatch: PropTypes.func,
    products: PropTypes.array,
    apiEnabled: PropTypes.bool,
    showSubscriberId: PropTypes.bool,
    clientsById: PropTypes.object,
};


const mapStateToProps = (state) => ({
    clients: state.clients.map((id) => state.clientsById[id]),
    clientToEdit: state.clientToEdit,
    activeQuery: searchQuerySelector(state),
    totalClients: state.totalClients,
    clientsById: state.clientsById,
});


const mapDispatchToProps = (dispatch) => ({
    selectClient: (id) => dispatch(selectClient(id)),
    editClient: (event) => dispatch(editClient(event)),
    saveClient: () => dispatch(postClient()),
    deleteClient: () => dispatch(deleteClient()),
    cancelEdit: (event) => dispatch(cancelEdit(event)),
    dispatch: dispatch,
});


export default connect(mapStateToProps, mapDispatchToProps)(Clients);
