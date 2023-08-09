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

class Clients extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any, context: any) {
        super(props, context);

        this.isFormValid = this.isFormValid.bind(this);
        this.save = this.save.bind(this);
        this.deleteClient = this.deleteClient.bind(this);
    }

    isFormValid() {
        let valid = true;
        const errors: any = {};

        if (!this.props.clientToEdit.name) {
            errors.name = [gettext('Please provide client name')];
            valid = false;
        }

        this.props.dispatch(setError(errors));
        return valid;
    }

    save(externalEvent: any) {
        if (externalEvent) {
            externalEvent.preventDefault();

            if (!this.isFormValid()) {
                return;
            }
        }

        this.props.saveClient('clients');
    }

    deleteClient(event: any) {
        event.preventDefault();

        if (confirm(gettext('Would you like to delete client: {{name}}', {name: this.props.clientToEdit.name}))) {
            this.props.deleteClient('clients');
        }
    }

    render() {
        const progressStyle: any = {width: '25%'};
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
    cancelEdit: PropTypes.func,
    isLoading: PropTypes.bool,
    activeQuery: PropTypes.string,
    totalClients: PropTypes.number,
    dispatch: PropTypes.func,
    clientsById: PropTypes.object,
};


const mapStateToProps = (state: any) => ({
    clients: state.clients.map((id: any) => state.clientsById[id]),
    clientToEdit: state.clientToEdit,
    activeQuery: searchQuerySelector(state),
    totalClients: state.totalClients,
    clientsById: state.clientsById,
});


const mapDispatchToProps = (dispatch: any) => ({
    selectClient: (id: any) => dispatch(selectClient(id)),
    editClient: (event: any) => dispatch(editClient(event)),
    saveClient: () => dispatch(postClient()),
    deleteClient: () => dispatch(deleteClient()),
    cancelEdit: (event: any) => dispatch(cancelEdit(event)),
    dispatch: dispatch,
});

const component: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(Clients);

export default component;
