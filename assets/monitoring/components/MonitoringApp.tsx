import React, {Fragment} from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {connect} from 'react-redux';
import {gettext} from 'utils';
import {
    newMonitoringProfile,
    fetchMonitoring,
    setCompany,
    toggleScheduleMode
} from '../actions';
import MonitoringPanel from './MonitoringPanel';
import ListBar from 'components/ListBar';
import DropdownFilter from 'components/DropdownFilter';


class MonitoringApp extends React.Component<any, any> {
    static propTypes: any;
    sections: Array<{name: string}>;

    constructor(props: any, context: any) {
        super(props, context);

        this.onChange = this.onChange.bind(this);
        this.getDropdownItems = this.getDropdownItems.bind(this);
        this.onSectionChange = this.onSectionChange.bind(this);

        this.sections = [
            {name: gettext('{{monitoring}} Profiles', window.sectionNames)},
            {name: gettext('Schedules')},
        ];

        this.state = {
            activeSection: this.sections[0].name,
            filter: {
                label:gettext('All Companies'),
                field: 'company'
            }
        };
    }

    isScheduleMode(sectionName: any = this.state.activeSection) {
        return sectionName === 'Schedules';
    }

    onSectionChange(sectionName: any) {
        if (sectionName !== this.state.activeSection) {
            this.setState({
                activeSection: sectionName,
                filter: {
                    label: this.isScheduleMode(sectionName) ? gettext('Companies with schedules') :
                        gettext('All Companies'),
                    field: 'company'
                }
            });

            this.props.toggleScheduleMode();
            this.onChange('company', null);
        }
    }

    getDropdownItems(filter: any) {
        const companies = this.isScheduleMode() ? this.props.monitoringListCompanies : this.props.companies;
        return (companies).map((item: any, i: number) => (<button
            key={i}
            className='dropdown-item'
            onClick={() => {this.onChange(filter.field, item._id);}}
        >{item.name}</button>));
    }

    getActiveQuery() {
        return {
            company: this.props.company ? [get(this.props.companies.find((c: any) => c._id === this.props.company), 'name')] :
                null,
        };
    }

    render() {
        const activeQuery = this.getActiveQuery();
        return (
            <Fragment>
                <ListBar
                    onNewItem={this.isScheduleMode() ? null : this.props.newMonitoringProfile}
                    buttonText={gettext('New {{monitoring}} Profile', window.sectionNames)}
                    noSearch>
                    <div className="toggle-button__group toggle-button__group--navbar ms-0 me-3">
                        {this.sections.map((section: any) => (
                            <button key={section.name}
                                className={'toggle-button' + (section.name === this.state.activeSection ? ' toggle-button--active' :
                                    '')}
                                onClick={this.onSectionChange.bind(null, section.name)}
                            >{gettext(section.name)}</button>
                        ))}
                    </div>
                </ListBar>
                <div className='align-items-center d-flex flex-sm-nowrap flex-wrap m-0 px-3 wire-column__main-header-agenda ps-3'>
                    <DropdownFilter
                        filter={this.state.filter}
                        getDropdownItems={this.getDropdownItems}
                        activeFilter={activeQuery}
                        toggleFilter={this.onChange}
                    />
                </div>
                <MonitoringPanel />
            </Fragment>

        );
    }

    onChange(field: any, value: any)
    {
        if (field === 'company') {
            this.props.setCompany(value);
        }

        this.props.fetchMonitoring();
    }
}

const mapStateToProps = (state: any) => ({
    companies: state.companies,
    company: state.company,
    monitoringListCompanies: state.monitoringListCompanies,
});

MonitoringApp.propTypes = {
    users: PropTypes.arrayOf(PropTypes.object),
    activeQuery: PropTypes.string,
    companies: PropTypes.arrayOf(PropTypes.object),
    errors: PropTypes.object,
    dispatch: PropTypes.func,
    fetchCompanies: PropTypes.func,
    setCompany: PropTypes.func,
    company: PropTypes.string,
    monitoringListCompanies: PropTypes.array,
    toggleScheduleMode: PropTypes.func,
    newMonitoringProfile: PropTypes.func,
    fetchMonitoring: PropTypes.func,
};

const mapDispatchToProps: any = {
    newMonitoringProfile,
    fetchMonitoring,
    setCompany,
    toggleScheduleMode,
};

export default connect(mapStateToProps, mapDispatchToProps)(MonitoringApp);
