
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
    associations: {[key: string]: IArticle};
    renditions?: {[key: string]: IRendition};
    slugline: string;
    headline: string;
    anpa_take_key?: string;
    source: string;
    versioncreated: string;
}
