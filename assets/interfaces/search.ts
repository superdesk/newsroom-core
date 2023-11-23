import {ITopic} from './topic';
import {INavigation} from './navigation';
import {IProduct} from './product';

export interface ISearchState {
    activeTopic?: ITopic['_id'];
    activeNavigation?: Array<INavigation['_id']>;
    activeQuery?: string;
    activeSortQuery?: string;
    activeFilter: {[key: string]: any};
    createdFilter: {
        from?: string;
        to?: string;
    };
    productId?: IProduct['_id'];
    navigations: Array<INavigation>;
    products: Array<IProduct>;
    activeView: 'list-view' | 'list-view-compact';
    advanced: {
        all: string;
        any: string;
        exclude: string;
        fields: Array<string>;
    };
}
