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
