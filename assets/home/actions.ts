import server from '../server';
import {errorHandler, recordAction} from 'utils';
import {pushNotification as wirePushNotification} from 'wire/actions';
import {get} from 'lodash';

export const INIT_DATA = 'INIT_DATA';
export function initData(data: any) {
    return {type: INIT_DATA, data};
}

function openItem(item: any) {
    return {type: OPEN_ITEM, item};
}

export const OPEN_ITEM = 'OPEN_ITEM';
export function openItemDetails(item: any) {
    return (dispatch: any) => {
        dispatch(openItem(item));
        recordAction(item, 'open');
    };
}

export const SET_ACTIVE = 'SET_ACTIVE';
export function setActive(cardId: any) {
    return {type: SET_ACTIVE, cardId};
}

export const SET_CARD_ITEMS = 'SET_CARD_ITEMS';
export function setCardItems(cardLabel: any, items: any) {
    return {type: SET_CARD_ITEMS, payload: {card: cardLabel, items: items}};
}

export const SET_MULTIPLE_CARD_ITEMS = 'SET_MULTIPLE_CARD_ITEMS';
export function getMultipleCardItems(itemsByCard: any) {
    return {type: SET_MULTIPLE_CARD_ITEMS, payload: itemsByCard};
}

export function fetchCompanyCardItems() {
    return (dispatch: any) => {
        return server.get('/card_items')
            .then((data: any) => dispatch(getMultipleCardItems(data._items)))
            .catch(errorHandler);
    };
}

export function fetchCardExternalItems(cardId: any, cardLabel: any) {
    return (dispatch: any) => {
        return server.get(`/media_card_external/${cardId}`)
            .then((data: any) => dispatch(
                setCardItems(cardLabel, get(data, '_items', []))
            ))
            .catch(errorHandler);
    };
}

export function pushNotification(push: any) {
    return (dispatch: any) => {
        if (push.event === 'items_deleted') {
            setTimeout(
                () => window.location.reload(),
                1000
            );
        } else {
            return dispatch(wirePushNotification(push));
        }
    };
}
