import CompanyProducts from './components/CompanyProducts';
import UserSavedSearches from './components/UserSavedSearches';
import CompanySavedSearches from './components/CompanySavedSearches';
import ProductStories from './components/ProductStories';
import Company from './components/Company';
import SubscriberActivity from './components/SubscriberActivity';
import ContentActivity from './components/ContentActivity';
import CompanyNewsApiUsage from './components/CompanyNewsApiUsage';
import ProductCompanies from './components/ProductCompanies';
import ExpiredCompanies from './components/ExpiredCompanies';
import SavedMyTopicsAndCompanyTopics from './components/SavedMyTopicsAndCompanyTopics';
import {REPORTS_NAMES} from './actions';


export const panels: any = {
    [REPORTS_NAMES.COMPANY_SAVED_SEARCHES]: CompanySavedSearches,
    [REPORTS_NAMES.USER_SAVED_SEARCHES]: UserSavedSearches,
    [REPORTS_NAMES.COMPANY_PRODUCTS]: CompanyProducts,
    [REPORTS_NAMES.PRODUCT_STORIES]: ProductStories,
    [REPORTS_NAMES.COMPANY]: Company,
    [REPORTS_NAMES.SUBSCRIBER_ACTIVITY]: SubscriberActivity,
    [REPORTS_NAMES.CONTENT_ACTIVITY]: ContentActivity,
    [REPORTS_NAMES.COMPANY_NEWS_API_USAGE]: CompanyNewsApiUsage,
    [REPORTS_NAMES.PRODUCT_COMPANIES]: ProductCompanies,
    [REPORTS_NAMES.EXPIRED_COMPANIES]: ExpiredCompanies,
    [REPORTS_NAMES.COMPANY_AND_USER_SAVED_SEARCHES]: SavedMyTopicsAndCompanyTopics
};
