export type TDatetime = string; // ISO8601 format

export interface IFilterGroup {
    single?: boolean;
    field: string;
    label: string;
    nested?: {
        parent: string;
        field: string;
        value: string;
        include_planning?: boolean;
    };
}

export interface ISection {
    _id: string;
    name: string;
    group: string;
    search_type: string;
}

export interface ICountry {
    value: string;
    text: string;
}
