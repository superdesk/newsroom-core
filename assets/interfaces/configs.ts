import {IArticle} from './content';

export interface FieldRenderProps {
    item?: IArticle;
    [key: string]: unknown;
}

export type FieldRenderComponent<P extends FieldRenderProps = FieldRenderProps> = React.ComponentType<P>;

export type Separator = '/' | '//' | '-';

// allowed component names
export enum ComponentName {
    VersionType = 'version_type',
    ServiceNames = 'service_names',
}

// component override: { field: "version", component: "version_type" }
export interface ComponentField {
    field: keyof IArticle;
    component: ComponentName;
    styles?: React.CSSProperties;
}

// styled wrapper: { field: <any valid config>, styles: {...} }
export interface StyledField {
    field: IDisplayFieldsConfig;
    styles: React.CSSProperties;
    component?: ComponentName;
}

export type IDisplayFieldsConfig =
    | keyof IArticle    // e.g. "source" or any item field name
    | Separator         // "/", "//", "-"
    | StyledField       // wraps a field (string/array/object) with styles
    | ComponentField    // component override for an existing item field
    | Array<IDisplayFieldsConfig>; // array of any of the above types


export interface IListConfig {
    subject?: {
        scheme?: Array<string> | string;
    };
    highlights?: {
        urgency?: Array<string>;
    };
    metadata_fields?: Array<IDisplayFieldsConfig>;
    compact_metadata_fields?: Array<IDisplayFieldsConfig>;
    show_list_action_icons?: {
        large?: boolean;
        compact?: boolean;
        mobile?: boolean;
    };
    abstract?: {displayed: boolean};
    wordcount?: {displayed: boolean};
    charcount?: {displayed: boolean};
    slugline?: {displayed: boolean};
    contacts?: {displayed: boolean};
}

export interface IPreviewConfig {
    slugline?: {displayed: boolean};
    abstract?: {displayed: boolean};
    category?: {displayed: boolean};
    subject?: {
        displayed: boolean;
        scheme?: Array<string> | string;
    };
    authors?: {displayed: boolean};
    byline?: {displayed: boolean};
    located?: {displayed: boolean};
    subjects?: {displayed: boolean};
    metadata_fields?: Array<IDisplayFieldsConfig>;
    disable_text_selection?: boolean;
}

interface IBaseUIConfig {
    _id: string;
    preview?: IPreviewConfig;
    details?: IPreviewConfig;
    list?: IListConfig;
    advanced_search_tabs?: {[tabId: string]: boolean};
    multi_select_topics?: boolean;
    enable_global_topics?: boolean;
}

export interface IHomeUIConfig extends IBaseUIConfig {
    _id: 'home';
    search?: boolean;
}

export interface IWireUIConfig extends IBaseUIConfig {
    _id: 'wire';
}

export interface IAgendaPreviewConfig extends IPreviewConfig {
    coverage_metadata_fields?: Array<string>;
}

export type AgendaFilterTypes = 'item_type' | 'calendar' | 'location' | 'region' | 'coverage_type' | 'coverage_status';

export interface ItemTypeFilterConfig {
    events_only?: boolean;
    planning_only?: boolean;
}

export interface IAgendaUIConfig extends IBaseUIConfig {
    _id: 'agenda';
    open_coverage_content_in_same_page?: boolean;
    subnav?: {
        filters?: Array<AgendaFilterTypes>;
        item_type?: ItemTypeFilterConfig;
    };
    preview?: IAgendaPreviewConfig;
    details?: IAgendaPreviewConfig;
}

export type IUIConfig = IHomeUIConfig | IWireUIConfig | IAgendaUIConfig;
