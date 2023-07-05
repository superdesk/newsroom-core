export interface IUser {
    user_type: 'administrator' | 'company_admin' | 'public';
    is_approved: boolean;
    is_enabled: boolean;
    company?: string;
    phone: string;
    email: string;
    name: string;
    is_validated: boolean;
    first_name: string;
    last_name: string;
    mobile: any;
    locale: any;
    role: any;
    manage_company_topics: boolean;
    expiry_alert: boolean;
    _id: string | null;
}
