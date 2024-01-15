import {IPublicAppState} from 'interfaces';

import {INIT_DATA} from 'actions';
import {SET_CARD_ITEMS, getMultipleCardItems} from 'home/actions';
import {CLOSE_MODAL, MODAL_FORM_VALID, RENDER_MODAL} from 'actions';

import {modalReducer} from 'reducers';
import homeReducer from 'home/reducers';

const initialState: IPublicAppState = {
    cards: [],
    itemsById: {},
    itemsByCard: {},
    uiConfig: {_id: 'home'},
    modal: undefined,
};

interface IAction {
    type?: string;
    payload?: any;
}

export function publicAppReducer(state: IPublicAppState = initialState, action: IAction): IPublicAppState {
    switch (action.type) {
    case INIT_DATA:
        return homeReducer(
            {
                ...state,
                cards: action.payload.cards,
                uiConfig: action.payload.ui_config,
                groups: action.payload.groups,
            },
            getMultipleCardItems(action.payload.items_by_card),
        );
    case SET_CARD_ITEMS:
        return homeReducer(state, action);
    case RENDER_MODAL:
    case MODAL_FORM_VALID:
    case CLOSE_MODAL:
        return {...state, modal: modalReducer(state.modal, action)};
    default:
        return state;
    }
}
