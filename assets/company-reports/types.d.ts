import type {IProduct, ICompany, ISection} from 'interfaces';

export type UserType = 'administrator' | 'internal' | 'public' | 'company_admin' | 'account_management';

export interface ICompanyReportsData {
    companies: Array<ICompany>;
    sections: Array<ISection>;
    api_enabled: boolean;
    current_user_type: UserType;
    products: Array<IProduct>;
}
