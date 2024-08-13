import {ITopic} from './topic';
import {INavigation} from './navigation';
import {IProduct} from './product';

export type ISearchSortValue = 'versioncreated:desc' | 'versioncreated:asc' | '_score' | '';

export interface ICreatedFilter {
    from?: string;
    to?: string;
    date_filter?: string;
}

export interface ISearchState {
    activeTopic?: ITopic['_id'];
    activeNavigation?: Array<INavigation['_id']>;
    activeQuery?: string;
    activeSortQuery?: ISearchSortValue;
    activeFilter: {[key: string]: any};
    createdFilter: ICreatedFilter;
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
