import {IUser} from './user';

export interface IDashboardCard {
    label: string;
    type: '6-text-only'
        | '4-picture-text'
        | '4-text-only'
        | '4-media-gallery'
        | '4-photo-gallery'
        | '1x1-top-news'
        | '2x2-top-news'
        | '3-text-only'
        | '3-picture-text'
        | '2x2-events'
        | '6-navigation-row';
    config: Dictionary<any>;
    order?: number;
    dashboard: string;
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
}
