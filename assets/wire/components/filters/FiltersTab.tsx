import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {isEmpty, cloneDeep, pickBy, assign, isEqual} from 'lodash';
import {gettext, toggleValue} from 'utils';

import NavCreatedPicker from './NavCreatedPicker';
import FilterGroup from './FilterGroup';

import {
    resetFilter,
    updateFilterStateAndURL,
} from 'search/actions';
import {
    searchFilterSelector,
    searchCreatedSelector,
} from 'search/selectors';

import {
    selectDate
} from '../../../agenda/actions';

import {resultsFilteredSelector} from 'search/selectors';

class FiltersTab extends React.Component<any, any> {
    static propTypes: any;

    constructor(props: any) {
        super(props);

        this.toggleGroup = this.toggleGroup.bind(this);
        this.getFilterGroups = this.getFilterGroups.bind(this);
        this.updateFilter = this.updateFilter.bind(this);
        this.setCreatedFilterAndSearch = this.setCreatedFilterAndSearch.bind(this);
        this.search = this.search.bind(this);
        this.reset = this.reset.bind(this);
        this.state = {
            groups: this.props.groups,
            activeFilter: cloneDeep(this.props.activeFilter),
            createdFilter: cloneDeep(this.props.createdFilter),
        };
    }

    componentDidUpdate(prevProps: any) {
        const newState: any = {};
        if (!isEqual(this.props.activeFilter, prevProps.activeFilter)) {
            newState.activeFilter = cloneDeep(this.props.activeFilter);
        }
        if (!isEqual(this.props.createdFilter, prevProps.createdFilter)) {
            newState.createdFilter = cloneDeep(this.props.createdFilter);
        }

        if (Object.keys(newState).length > 0) {
            this.setState(newState);
        }
    }

    toggleGroup(event: any, group: any) {
        event.preventDefault();
        this.setState({groups: this.props.groups.map((_group: any) =>
            _group === group ? Object.assign({}, _group, {isOpen: !_group.isOpen}) : _group
        )});
    }

    updateFilter(field: any, key: any, single: any) {
        // The `value` can be an Array
        const values = Array.isArray(key) ? key : [key];
        const currentFilters = cloneDeep(this.state.activeFilter);

        for (const _value of values) {
            currentFilters[field] = toggleValue(currentFilters[field], _value);

            if (!_value || !currentFilters[field] || currentFilters[field].length === 0) {
                delete currentFilters[field];
            } else if (single) {
                currentFilters[field] = currentFilters[field].filter(
                    (val: any) => val === _value
                );
            }
        }

        this.setState({activeFilter: currentFilters});
    }

    setCreatedFilterAndSearch(createdFilter: any) {
        const created = pickBy(
            assign(
                cloneDeep(this.state.createdFilter),
                createdFilter
            )
        );

        this.setState({createdFilter: created});
    }

    getFilterGroups() {
        return this.state.groups.map((group: any) => {
            if (this.props.aggregations == null) {
                return null;
            }

            return (
                <FilterGroup
                    key={group.label}
                    group={group}
                    activeFilter={this.state.activeFilter}
                    aggregations={this.props.aggregations}
                    toggleGroup={this.toggleGroup}
                    toggleFilter={this.updateFilter}
                    isLoading={this.props.isLoading}
                />
            );
        });
    }

    search(event: any) {
        event.preventDefault();
        this.props.updateFilterStateAndURL(this.state.activeFilter, this.state.createdFilter);
        this.props.fetchItems();
    }

    reset(event: any) {
        event.preventDefault();
        this.setState({activeFilter: {}, createdFilter: {}});
        this.props.resetFilter();
        this.props.fetchItems();
    }

    render() {
        const {activeFilter, createdFilter} = this.state;
        const isResetActive = Object.keys(activeFilter).find((key: any) => !isEmpty(activeFilter[key]))
            || Object.keys(createdFilter).find((key: any) => !isEmpty(createdFilter[key]));

        return (
            <div className="d-contents">
                <div className='tab-pane__inner'>
                    {this.getFilterGroups().filter((group: any) => !!group).concat([(
                        <NavCreatedPicker
                            key="created"
                            createdFilter={createdFilter}
                            setCreatedFilter={this.setCreatedFilterAndSearch}
                            context = {this.props.context}
                        />
                    )])}
                </div>
                {!isResetActive && !this.props.resultsFiltered ? null : ([
                    <div className='tab-pane__footer tab-pane__footer--inline' key='footer-buttons'>

                        <button
                            className='nh-button nh-button--secondary'
                            onClick={this.reset}
                            data-test-id="filter-panel--clear-btn"
                        >
                            {gettext('Clear')}
                        </button>
                        <button
                            className='nh-button nh-button--primary'
                            onClick={this.search}
                            data-test-id="filter-panel--search-btn"
                        >
                            {gettext('Search')}
                        </button>
                    </div>
                ])}
            </div>
        );
    }
}

FiltersTab.propTypes = {
    aggregations: PropTypes.object,
    activeFilter: PropTypes.object,
    createdFilter: PropTypes.object.isRequired,
    resultsFiltered: PropTypes.bool.isRequired,
    isLoading: PropTypes.bool,

    resetFilter: PropTypes.func.isRequired,
    updateFilterStateAndURL: PropTypes.func.isRequired,
    fetchItems: PropTypes.func.isRequired,
    groups: PropTypes.array,
    selectDate: PropTypes.func,
    context: PropTypes.string,
};

const mapStateToProps = (state: any) => ({
    aggregations: state.aggregations,
    activeFilter: searchFilterSelector(state),
    createdFilter: searchCreatedSelector(state),
    resultsFiltered: resultsFilteredSelector(state),
    isLoading: state.loadingAggregations,
    context: state.context
});

const mapDispatchToProps: any = {
    resetFilter,
    updateFilterStateAndURL,
    selectDate,
};

export default connect(mapStateToProps, mapDispatchToProps)(FiltersTab);
