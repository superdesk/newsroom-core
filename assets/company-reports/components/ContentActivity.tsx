import React, {Fragment} from 'react';
import {connect} from 'react-redux';

import {gettext, formatTime} from '../../utils';
import {fetchReport, REPORTS} from '../actions';

import ReportsTable from './ReportsTable';
import {ContentActivityFilters} from './ContentActivityFilters';
import {type Dictionary} from 'globals';


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

    fetchReport: typeof fetchReport;
    reportParams: Dictionary<any>;
}

class ContentActivity extends React.Component<IProps, any> {
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

    exportToCSV = () => {
        this.props.fetchReport(
            REPORTS['content-activity'],
            false,
            true
        );
    };

    renderSorted = (elems: Array<string>) => {
        return elems
            .sort()
            .map((name) => (
                <Fragment key={name}>
                    {name}<br />
                </Fragment>
            ));
    };

    renderNamesSorted = (elems: Array<{name: string}>) => {
        return this.renderSorted((elems || []).map((x) => x.name));
    };

    renderCompaniesSorted = (companiesIds: Array<number>) => {
        const {companies} = this.props;
        const companiesNames = companiesIds
            .map((companyId) => companies.find(x => x._id === companyId)?.name)
            .filter(x => x !== undefined);

        return this.renderSorted(companiesNames);
    };

    renderList() {
        const {results} = this.props;
        const actions = this.getFilteredActions();

        if (results?.length > 0) {
            return results.map((item: any) => {
                const itemActions = item?.aggs?.actions || {};

                return (
                    <tr key={item._id}>
                        <td>{formatTime(item?.versioncreated || '')}</td>
                        <td>{item.headline || ''}</td>
                        <td>{item.anpa_take_key || ''}</td>
                        <td>{this.renderNamesSorted(item?.place)}</td>
                        <td>{this.renderNamesSorted(item?.service)}</td>
                        <td>{this.renderNamesSorted(item?.subject)}</td>
                        <td>{item.source}</td>
                        <td>{this.renderCompaniesSorted(item?.aggs?.companies || [])}</td>
                        <td>{item?.aggs?.total || 0}</td>
                        {actions.includes('download') && <td>{itemActions?.download || 0}</td>}
                        {actions.includes('copy') && <td>{itemActions?.copy || 0}</td>}
                        {actions.includes('share') && <td>{itemActions?.share || 0}</td>}
                        {actions.includes('print') && <td>{itemActions?.print || 0}</td>}
                        {actions.includes('open') && <td>{itemActions?.open || 0}</td>}
                        {actions.includes('preview') && <td>{itemActions?.preview || 0}</td>}
                        {actions.includes('clipboard') && <td>{itemActions?.clipboard || 0}</td>}
                        {actions.includes('api') && <td>{itemActions?.api || 0}</td>}
                    </tr>
                );
            });
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
    reportParams: state.reportParams
});

const mapDispatchToProps: any = {
    fetchReport
};

export default connect(mapStateToProps, mapDispatchToProps)(ContentActivity);
