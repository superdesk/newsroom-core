import {IUser} from './user';
import {ICompany} from './company';
import {INavigation} from './navigation';

export interface IProduct {
    _id: string;
    name: string;
    description?: string;
    sd_product_id?: string;
    query?: string;
    planning_item_query?: string;
    is_enabled: boolean;
    navigations: Array<INavigation['_id']>;
    companies?: Array<ICompany['_id']>;
    product_type: 'wire' | 'agenda';
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
}
