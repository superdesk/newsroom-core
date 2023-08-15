import {IUser} from './user';

export interface ISectionFilter {
    name: string;
    description?: string;
    sd_product_id?: string;
    query?: string;
    is_enabled: boolean;
    filter_type: 'wire' | 'agenda';
    search_type: 'wire' | 'agenda';
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
}
