import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import {connect} from 'react-redux';
import {gettext, fullDate, upperCaseFirstCharacter} from 'utils';
import {get} from 'lodash';
import ReportsTable from './ReportsTable';
import DropdownFilter from '../../components/DropdownFilter';
import CalendarButton from '../../components/CalendarButton';
import {toggleFilterAndQuery, fetchReport, REPORTS, runReport} from '../actions';

class SubscriberActivity extends React.Component<any, any> {
    static propTypes: any;
    companies: Array<any>;
    filters: Array<any>;
    previousScrollTop: number;
    constructor(props: any, context: any) {
        super(props, context);

        this.companies = [...this.props.companies.map((c: any) => ({...c, 'label': c.name}))];
        this.state = {company: this.props.companies[0]};

        this.filters = [{
            label: gettext('All Companies'),
            field: 'company'
        },
        {
            label: gettext('All Actions'),
            field: 'action'
        },
        {
            label: gettext('All Sections'),
            field: 'section'
        }];
        this.getDropdownItems = this.getDropdownItems.bind(this);
        this.onScroll = this.onScroll.bind(this);
        this.onFromDateChange = this.onFromDateChange.bind(this);
        this.onEndDateChange = this.onEndDateChange.bind(this);
        this.previousScrollTop = 0;
    }

    componentWillMount() {
        // Run report on initial loading with default filters
        this.props.runReport();
    }

    componentWillReceiveProps(nextProps: any) {
        if (this.props.reportParams !== nextProps.reportParams) {
            // Filtering done
            this.previousScrollTop = 0;
        }
    }

    getDropdownItems(filter: any) {
        const {toggleFilterAndQuery, sections, apiEnabled} = this.props;
        let getName = (text: any) => (text);
        let itemsArray: Array<any> = [];
        // Company is not filtered, always show full list
        switch(filter.field) {
        case 'company':
            itemsArray= this.companies;
            break;

        case 'action':
            itemsArray = [{
                name: 'download'
            },
            {
                name: 'download audio'
            },
            {
                name: 'download video'
            },
            {
                name: 'download picture'
            },
            {
                name: 'copy'
            },
            {
                name: 'share'
            },
            {
                name: 'print'
            },
            {
                name: 'open'
            },
            {
                name: 'preview'
            },
            {
                name: 'clipboard'
            }];

            if (apiEnabled) {
                itemsArray.push({
                    name: 'api retrieval',
                    value: 'api'
                });}

            getName = upperCaseFirstCharacter;
            break;

        case 'section':
            itemsArray = sections;
            break;
        }


        return itemsArray.map((item: any, i: any) => (<button
            key={i}
            className='dropdown-item'
            onClick={() => toggleFilterAndQuery(filter.field, item.value || item.name)}
        >{getName(item.name)}</button>));
    }

    getFilterLabel(filter: any, activeFilter: any) {
        if (activeFilter[filter.field]) {
            if (activeFilter.action === 'api' && filter.field === 'action')
                return 'api retrieval';
            return activeFilter[filter.field];
        } else {
            return filter.label;
        }
    }

    onScroll(event: any) {
        if (this.props.isLoading) {
            return;
        }

        event.stopPropagation();
        event.preventDefault();
        const node = event.target;
        if (node && (node.scrollTop + node.offsetHeight + 100 >= node.scrollHeight) &&
            node.scrollTop > (this.previousScrollTop + 2)) {
            this.props.fetchReport(REPORTS['subscriber-activity'], true);
            this.previousScrollTop = node.scrollTop;
        }
    }

    onFromDateChange(value: any) {
        this.props.toggleFilterAndQuery('date_from', value);

    }

    onEndDateChange(value: any) {
        this.props.toggleFilterAndQuery('date_to', value);
    }

    render() {
        const {results, print, reportParams, toggleFilterAndQuery} = this.props;
        const headers = [gettext('Company'), gettext('Section'), gettext('Item'), gettext('Published'), gettext('Place'), gettext('Slugline'), gettext('Takekey'), gettext('Service'), gettext('Subject'), gettext('Action'), gettext('User'), gettext('Time')];
        const list = get(results, 'length', 0) > 0 ? results.map((item: any) =>
            <tr key={item._id}>
                <td>{item.company}</td>
                <td>{item.section}</td>
                <td>
                    {get(item, 'item.item_href', null) &&
                        <a href={get(item, 'item.item_href', '#')} target="_blank">{get(item, 'item.item_text')}</a>}
                    {!get(item, 'item.item_href') && <span>{get(item, 'item.item_text')}</span>}
                    {get(item, 'association.href', null) &&
                        ' / '
                    }
                    {get(item, 'association.href', null) &&
                        <a href={get(item, 'association.href', '#')}
                            target="_blank">{get(item, 'association.text')}</a>}
                </td>
                <td>{fullDate(get(item, 'item.published'))}</td>
                <td>{get(item, 'item.place')}</td>
                <td>{get(item, 'item.slugline')}</td>
                <td>{get(item, 'item.anpa_take_key')}</td>
                <td>{get(item, 'item.service')}</td>
                <td>{get(item, 'item.subject')}</td>
                <td>{item.action}</td>
                <td>{item.user}</td>
                <td>{fullDate(item.versioncreated)}</td>
            </tr>
        ) : ([(<tr key='no_data_row'>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td>{gettext('No Data')}</td>
            <td></td>
            <td></td>
            <td></td>
        </tr>)]);

        let filterNodes = this.filters.map((filter: any) => (
            <DropdownFilter
                key={filter.label}
                filter={filter}
                getDropdownItems={this.getDropdownItems}
                activeFilter={reportParams}
                getFilterLabel={this.getFilterLabel}
                toggleFilter={toggleFilterAndQuery}
            />
        ));
        filterNodes = [
            ...filterNodes,
            (<CalendarButton
                key='subscriver_activity_from'
                labelClass='ms-3 d-flex align-items-center'
                label={gettext('FROM:')}
                selectDate={this.onFromDateChange}
                activeDate={get(reportParams, 'date_from') || moment()} />),
            (<CalendarButton
                key='subscriver_activity_to'
                labelClass='d-flex align-items-center'
                label={gettext('TO:')}
                selectDate={this.onEndDateChange}
                activeDate={get(reportParams, 'date_to') || moment()} />)
        ];
        filterNodes.push(<button
            key='subscriver_activity_export'
            className="nh-button nh-button--secondary ms-auto me-3"
            type="button"
            onClick={() => {this.props.fetchReport(REPORTS['subscriber-activity'], false, true);}}>Export to CSV</button>);

        const filterSection = (<div key='report_filters' className="align-items-center d-flex flex-sm-nowrap flex-wrap m-0 px-3 wire-column__main-header-agenda">{filterNodes}</div>);

        return [filterSection,
            (<ReportsTable key='report_table' headers={headers} rows={list} print={print} onScroll={this.onScroll} />)];
    }
}

SubscriberActivity.propTypes = {
    results: PropTypes.array,
    print: PropTypes.bool,
    companies: PropTypes.array,
    runReport: PropTypes.func,
    toggleFilterAndQuery: PropTypes.func,
    isLoading: PropTypes.bool,
    fetchReport: PropTypes.func,
    reportParams: PropTypes.object,
    sections: PropTypes.array,
    apiEnabled: PropTypes.bool,
};

const mapStateToProps = (state: any) => ({
    companies: state.companies,
    reportParams: state.reportParams,
    isLoading: state.isLoading,
    sections: state.sections,
});

const mapDispatchToProps: any = {toggleFilterAndQuery, fetchReport, runReport};

export default connect(mapStateToProps, mapDispatchToProps)(SubscriberActivity);
