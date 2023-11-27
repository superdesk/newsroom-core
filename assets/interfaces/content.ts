
export type IContentType = 'text' | 'picture' | 'video' | 'audio';

export interface IRendition {
    href: string;
    mimetype: string;
    media?: string;
    width?: number;
    height?: number;
}

export interface IArticle {
    _id: string;
    guid: string;
    type: IContentType;
    ancestors?: Array<IArticle['_id']>;
    nextversion?: IArticle['_id'];
    associations?: {[key: string]: IArticle | null};
    renditions?: {[key: string]: IRendition};
    slugline: string;
    headline: string;
    anpa_take_key?: string;
    source: string;
    versioncreated: string;
}
