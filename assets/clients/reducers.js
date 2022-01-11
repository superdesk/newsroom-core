import {
    EDIT_CLIENT,
    GET_CLIENTS,
    NEW_CLIENT,
    QUERY_CLIENTS,
    SELECT_CLIENT,
    CANCEL_EDIT,
    INIT_VIEW_DATA,
} from './actions';

import {searchReducer} from 'search/reducers';

const initialState = {
    query: null,
    clients: [],
    clientsById: {},
    totalClients: null,
    activeQuery: null,
    search: searchReducer(),
};

function setupClients(clientList, state) {
    const clientsById = {};
    const clients = clientList.map((client) => {
        clientsById[client._id] = client;
        return client._id;
    });
    return {
        ...state,
        clientsById,
        clients,
        totalClients: clientList.length,
    };
}

export default function clientReducer(state = initialState, action) {
    switch (action.type) {

    case SELECT_CLIENT: {
        const defaultClient = {
            name: '',
        };

        return {
            ...state,
            activeClientId: action.id || null,
            clientToEdit: action.id ? Object.assign(defaultClient, state.clientsById[action.id]) : null,
            errors: null,
        };
    }

    case EDIT_CLIENT: {
        const target = action.event.target;
        const field = target.name;
        let client = state.clientToEdit;
        client[field] = target.value;
        return {...state, clientToEdit: client, errors: null};
    }

    case NEW_CLIENT: {
        const newClient =  {
            name: '',
            secret_key: '',
        };

        return {...state, clientToEdit: newClient, errors: null};
    }

    case CANCEL_EDIT: {
        return {...state, clientToEdit: null, errors: null};
    }

    case QUERY_CLIENTS:
        return {...state,
            activeQuery: state.query};

    case GET_CLIENTS:
        return setupClients(action.data, state);

    case INIT_VIEW_DATA: {
        const nextState = {
            ...state,
            products: action.data.products,
            sections: action.data.sections,
            apiEnabled: action.data.api_enabled || false,
            ui_config: action.data.ui_config,
        };

        return setupClients(action.data.clients, nextState);
    }

    default: {
        const search = searchReducer(state.search, action);

        if (search !== state.search) {
            return {...state, search};
        }

        return state;
    }
    }    
}
