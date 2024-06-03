import React from 'react';
import {connect} from 'react-redux';
import {
    setActiveReport,
    runReport,
    REPORTS_NAMES,
    printReport,
    toggleFilterAndQuery,
} from '../actions';
import {gettext} from 'utils';
import {panels} from '../utils';

import type {IProduct, ICompany} from 'interfaces';
import type {UserType} from 'company-reports/types';

interface IProps {
    activeReport: 'string';
    results: Array<any>;
    companies: Array<ICompany>;
    products: Array<IProduct>;
    isLoading: boolean;
    apiEnabled: boolean;
    runReport: typeof runReport;
    printReport: typeof printReport;
    setActiveReport: (value: string) => void;
    currentUserType: UserType;
}


const adminReports = [
    {value: '', text: gettext('Select a report')},
    {value: REPORTS_NAMES.COMPANY_SAVED_SEARCHES, text: gettext('Saved searches per company')},
    {value: REPORTS_NAMES.USER_SAVED_SEARCHES, text: gettext('Saved searches per user')},
    {value: REPORTS_NAMES.COMPANY_PRODUCTS, text: gettext('Products per company')},
    {value: REPORTS_NAMES.PRODUCT_STORIES, text: gettext('Stories per product')},
    {value: REPORTS_NAMES.COMPANY, text: gettext('Company')},
    {value: REPORTS_NAMES.SUBSCRIBER_ACTIVITY, text: gettext('Subscriber activity')},
    {value: REPORTS_NAMES.CONTENT_ACTIVITY, text: gettext('Content activity')},
    {value: REPORTS_NAMES.PRODUCT_COMPANIES, text: gettext('Companies per Product')},
    {value: REPORTS_NAMES.EXPIRED_COMPANIES, text: gettext('Expired companies')},
];

const companyAdminReports = [
    {value: '', text: gettext('Select a report')},
    {value: REPORTS_NAMES.COMPANY_SAVED_SEARCHES, text: gettext('Saved searches per company')},
];

const getReportsByUserType = (userType: UserType): Array<any> => {
    switch (userType) {
    case 'company_admin':
        return companyAdminReports;
    default:
        return adminReports;
    }
};


class CompanyReportsApp extends React.Component<IProps> {
    getPanel = () => {
        const Panel = panels[this.props.activeReport];
        return Panel && this.props.results && <Panel key="panel" {...this.props}/>;
    };

    reportOptions = () => {
        const {apiEnabled, currentUserType} = this.props;
        const options = getReportsByUserType(currentUserType);

        if (currentUserType !== 'company_admin') {
            return !apiEnabled ? options :
                [
                    ...options,
                    {value: REPORTS_NAMES.COMPANY_NEWS_API_USAGE, text: gettext('Company News API Usage')},
                ];
        }

        return options;
    };

    render() {
        return (
            [
                <section key="header" className="content-header">
                    <nav className="content-bar navbar content-bar--side-padding">
                        <div className='content-bar__left'>
                            <select
                                className="form-control"
                                id={'company-reports'}
                                name={'company-reports'}
                                value={this.props.activeReport || ''}
                                onChange={(event) => this.props.setActiveReport(event.target.value)}>
                                {this
                                    .reportOptions()
                                    .map((option: any) =>
                                        <option key={option.value} value={option.value}>
                                            {option.text}
                                        </option>
                                    )}
                            </select>
                        </div>

                        <div className="content-bar__right">
                            {this.props.activeReport && <button
                                className='nh-button nh-button--secondary'
                                type='button'
                                onClick={this.props.runReport}>
                                {gettext('Run report')}
                            </button>}
                            {this.props.activeReport && <button
                                className='nh-button nh-button--secondary ms-2'
                                type='button'
                                onClick={this.props.printReport} >
                                {gettext('Print report')}
                            </button>}
                        </div>
                    </nav>
                </section>,
                this.getPanel()
            ]
        );
    }
}

const mapStateToProps = (state: any) => ({
    activeReport: state.activeReport,
    results: state.results,
    companies: state.companies,
    apiEnabled: state.apiEnabled,
    reportParams: state.reportParams,
    isLoading: state.isLoading,
    resultHeaders: state.resultHeaders,
    products: state.products,
    currentUserType: state.currentUserType
});

const mapDispatchToProps: any = {
    setActiveReport,
    runReport,
    printReport,
    toggleFilterAndQuery,
};

const component: React.ComponentType<IProps> = connect(mapStateToProps, mapDispatchToProps)(CompanyReportsApp);

export default component;
