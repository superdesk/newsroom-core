export interface INotification {
    _id: string;
    resource: string;
    action: string;
    user: string;
    item: string;
    data: any;
}