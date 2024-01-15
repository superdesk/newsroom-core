import {IDashboardCard} from './dashboard';
import {IArticle} from './content';
import {IHomeUIConfig} from './configs';
import {IModalState} from 'reducers';

export interface IPublicAppState {
    cards: Array<IDashboardCard>;
    itemsById: {[itemId: string]: IArticle};
    itemsByCard: {[cardId: string]: Array<IArticle>};
    uiConfig: IHomeUIConfig;
    modal?: IModalState;
}
