import {IUser} from './user';

export interface INavigation {
    _id: string;
    name: string;
    description?: string;
    is_enabled: boolean;
    order?: number;
    product_type: 'wire' | 'agenda';
    tile_images: Array<string>;
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
}
