import {IUser} from './user';

export interface IDashboardCard {
    _id: string;
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
    config: {
        product: string;
        size?: number;
        more_url?: string;
        more_url_label?: string;
        events?: Array<{
            startDate?: string;
            endDate?: string;
            file_url?: string;
            headline: string;
            location: string;
            abstract: string;
        }>;
        [key: string]: any;
    };
    order?: number;
    dashboard: string;
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
}
