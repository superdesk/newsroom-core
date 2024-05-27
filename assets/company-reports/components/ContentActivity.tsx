import React, {Fragment} from 'react';
import {connect} from 'react-redux';
import {keyBy} from 'lodash';

import {gettext, formatTime} from '../../utils';
import {fetchReport, REPORTS} from '../actions';

import ReportsTable from './ReportsTable';
import {ContentActivityFilters} from './ContentActivityFilters';


interface IReportAction {
    download?: number;
    copy?: number;
    share?: number;
    print?: number;
    open?: number;
    preview?: number;
    clipboard?: number;
    api?: number;
}

interface IResultItem {
    _id: string;
    versioncreated: string;
    headline: string;
    anpa_take_key: string;
    source: string;
    place: Array<{name: string}>;
    service: Array<{name: string}>;
    subject: Array<{name: string}>;
    aggs?: {
        actions?: IReportAction;
        total?: number;
        companies?: Array<string>;
    };
}

interface IProps {
    results: Array<IResultItem>,
    print: boolean;
    companies: Array<any>;
    isLoading: boolean;
    apiEnabled: boolean;

    fetchReport: typeof fetchReport;

    reportParams: Dictionary<any>;
}

class ContentActivity extends React.Component<IProps, any> {
    constructor(props: any) {
        super(props);

        this.state = {
            results: []
        };
    }

    UNSAFE_componentWillReceiveProps(nextProps: any) {
        if (this.props.results !== nextProps.results) {
            this.updateResults(nextProps);
        }
    }

    getFilteredActions() {
        const {reportParams} = this.props;
        const defaultActions = ['download', 'copy', 'share', 'print', 'open', 'preview', 'clipboard', 'api'];

        return reportParams?.action || defaultActions;
    }

    getHeaders() {
        const headers = [
            gettext('Published'),
            gettext('Headline'),
            gettext('Take Key'),
            gettext('Place'),
            gettext('Category'),
            gettext('Subject'),
            gettext('Source'),
            gettext('Companies'),
            gettext('Actions'),
        ];
        const actions = this.getFilteredActions();

        actions.includes('download') && headers.push(gettext('Download'));
        actions.includes('copy') && headers.push(gettext('Copy'));
        actions.includes('share') && headers.push(gettext('Share'));
        actions.includes('print') && headers.push(gettext('Print'));
        actions.includes('open') && headers.push(gettext('Open'));
        actions.includes('preview') && headers.push(gettext('Preview'));
        actions.includes('clipboard') && headers.push(gettext('Clipboard'));
        actions.includes('api') && headers.push(gettext('API retrieval'));

        return headers;
    }

    updateResults(props: any) {
        const companies = keyBy(this.props.companies, '_id');
        const results = props.results.map(
            (item: IResultItem) => {
                const actions = item?.aggs?.actions || {};

                return {
                    _id: item._id,
                    versioncreated: formatTime(item?.versioncreated || ''),
                    headline: item?.headline || '',
                    anpa_take_key: item?.anpa_take_key || '',
                    source: item?.source || '',
                    place: (item?.place || [])
                        .map((place) => place.name)
                        .sort(),
                    service: (item?.service || [])
                        .map((service) => service.name)
                        .sort(),
                    subject: (item?.subject || [])
                        .map((subject) => subject.name)
                        .sort(),
                    total: item?.aggs?.total || 0,
                    companies: (item?.aggs?.companies || [])
                        .map((company) => companies[company].name)
                        .sort(),
                    actions: {
                        download: actions?.download || 0,
                        copy: actions?.copy || 0,
                        share: actions?.share || 0,
                        print: actions?.print || 0,
                        open: actions?.open || 0,
                        preview: actions?.preview || 0,
                        clipboard: actions?.clipboard || 0,
                        api: actions?.api || 0,
                    }
                };
            }
        );
        this.setState({results});
    }

    exportToCSV = () => {
        this.props.fetchReport(
            REPORTS['content-activity'],
            false,
            true
        );
    };

    renderList() {
        const {results} = this.state;
        const actions = this.getFilteredActions();

        if (results?.length > 0) {
            return results.map((item: any) =>
                <tr key={item._id}>
                    <td>{item.versioncreated}</td>
                    <td>{item.headline}</td>
                    <td>{item.anpa_take_key}</td>
                    <td>{item.place.map((place: any) => (
                        <Fragment key={place}>
                            {place}<br />
                        </Fragment>
                    ))}</td>
                    <td>{item.service.map((service: any) => (
                        <Fragment key={service}>
                            {service}<br />
                        </Fragment>
                    ))}</td>
                    <td>{item.subject.map((subject: any) => (
                        <Fragment key={subject}>
                            {subject}<br />
                        </Fragment>
                    ))}</td>
                    <td>{item.source}</td>
                    <td>{item.companies.map((company: any) => (
                        <Fragment key={company}>
                            {company}<br />
                        </Fragment>
                    ))}</td>
                    <td>{item.total}</td>
                    {actions.includes('download') && <td>{item.actions.download}</td>}
                    {actions.includes('copy') && <td>{item.actions.copy}</td>}
                    {actions.includes('share') && <td>{item.actions.share}</td>}
                    {actions.includes('print') && <td>{item.actions.print}</td>}
                    {actions.includes('open') && <td>{item.actions.open}</td>}
                    {actions.includes('preview') && <td>{item.actions.preview}</td>}
                    {actions.includes('clipboard') && <td>{item.actions.clipboard}</td>}
                    {actions.includes('api') && <td>{item.actions.api}</td>}
                </tr>
            );
        }

        return [
            <tr key='no_data_row'>
                <td colSpan={this.getHeaders().length}>{gettext('No Data')}</td>
            </tr>,
        ];
    }

    render() {
        const {print} = this.props;

        return (
            <Fragment>
                <div className="align-items-center d-flex flex-sm-nowrap flex-wrap m-0 px-3 wire-column__main-header-agenda">
                    <ContentActivityFilters />

                    <button
                        key='content_activity_export'
                        className="nh-button nh-button--secondary ms-auto me-3"
                        type="button"
                        onClick={this.exportToCSV}
                    >
                        {gettext('Export to CSV')}
                    </button>
                </div>
                <ReportsTable
                    key='report_table'
                    headers={this.getHeaders()}
                    rows={this.renderList()}
                    print={print}
                    tableClass='content-activity__table'
                />
            </Fragment>
        );
    }
}

const mapStateToProps = (state: any) => ({
    companies: state.companies,
    reportParams: state.reportParams,
    isLoading: state.isLoading
});

const mapDispatchToProps: any = {
    fetchReport
};

export default connect(mapStateToProps, mapDispatchToProps)(ContentActivity);
