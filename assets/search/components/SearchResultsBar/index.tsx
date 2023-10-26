import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {searchParamsSelector, navigationsByIdSelector, filterGroupsByIdSelector} from '../../selectors';
import {getAdvancedSearchFields} from '../../utils';
import {
    toggleNavigation,
    toggleAdvancedSearchField,
    setAdvancedSearchKeywords,
    toggleFilter,
    setCreatedFilter,
    resetSearchParamsAndUpdateURL,
    clearAdvancedSearchParams,
    resetFilter,
    deselectMyTopic,
} from '../../actions';

import {Dropdown} from './../../../components/Dropdown';

import {SearchResultTagsList} from './SearchResultTagsList';
import NewItemsIcon from '../NewItemsIcon';


class SearchResultsBarComponent extends React.Component<any, any> {
    private sortValues: Array<{value: string; sortFunction: () => void;}>;
    private topicNotNull: boolean;

    static propTypes: any;
    static defaultProps: any;
    constructor(props: any) {
        super(props);

        this.topicNotNull = new URLSearchParams(window.location.search).get('topic') != null;
        this.sortValues = [
            {
                value: gettext('Date ↑'),
                sortFunction: () => this.setSortQuery('versioncreated:desc'),
            },
            {
                value: gettext('Date ↓'),
                sortFunction: () => this.setSortQuery('versioncreated:asc'),
            },
            {
                value: gettext('Relevance'),
                sortFunction: () => this.setSortQuery('_score'),
            },
        ];

        this.state = {
            isTagSectionShown: this.props.initiallyOpen || this.topicNotNull,
            sortValue: this.sortValues[0].value,
        };

        this.toggleTagSection = this.toggleTagSection.bind(this);
        this.toggleNavigation = this.toggleNavigation.bind(this);
        this.setQuery = this.setQuery.bind(this);
        this.setSortQuery = this.setSortQuery.bind(this);
        this.setAdvancedSearchKeywords = this.setAdvancedSearchKeywords.bind(this);
        this.toggleAdvancedSearchField = this.toggleAdvancedSearchField.bind(this);
        this.clearAdvancedSearchParams = this.clearAdvancedSearchParams.bind(this);
        this.setCreatedFilter = this.setCreatedFilter.bind(this);
        this.toggleFilter = this.toggleFilter.bind(this);
        this.resetFilter = this.resetFilter.bind(this);
    }

    componentDidUpdate(prevProps: any): void {
        if (prevProps.initiallyOpen != this.props.initiallyOpen) {
            this.setState({
                isTagSectionShown: this.props.initiallyOpen || this.topicNotNull,
            });
        }
    }

    toggleTagSection() {
        this.setState((prevState: any) => ({isTagSectionShown: !prevState.isTagSectionShown}));
    }

    toggleNavigation(navigation: any) {
        this.props.toggleNavigation(navigation);
        this.props.refresh();
    }

    setQuery(query: any) {
        this.props.setQuery(query);
        this.props.refresh();
    }

    setSortQuery(sortQuery: string) {
        this.props.setSortQuery(sortQuery);
        this.props.refresh();
    }

    setAdvancedSearchKeywords(field: any, keywords: any) {
        this.props.setAdvancedSearchKeywords(field, keywords);
        this.props.refresh();
    }

    toggleAdvancedSearchField(field: any) {
        this.props.toggleAdvancedSearchField(field);
        this.props.refresh();
    }

    clearAdvancedSearchParams() {
        this.props.clearAdvancedSearchParams();
        this.props.refresh();
    }

    setCreatedFilter(filter: any) {
        this.props.setCreatedFilter(filter);
        this.props.refresh();
    }

    toggleFilter(key: any, value: any, single: any) {
        this.props.toggleFilter(key, value, single);
        this.props.refresh();
    }

    resetFilter() {
        this.props.resetFilter();
        this.props.refresh();
    }

    render() {
        const {isTagSectionShown} = this.state;
        const numberFormatter = (new Intl.NumberFormat(undefined, {style: 'decimal'}));

        return (
            <React.Fragment>
                <div
                    data-test-id="search-results-bar"
                    className="d-contents"
                >
                    {!this.props.showTotalItems ? null : (
                        <div className="navbar navbar--flex line-shadow-end--light navbar--search-results">
                            {!this.props.showTotalItems ? null : (
                                <div className="search-result-count">
                                    {this.props.totalItems === 1 ?
                                        gettext('1 result') :
                                        gettext('{{ count }} results', {
                                            count: numberFormatter.format(this.props.totalItems || 0)
                                        })
                                    }
                                </div>
                            )}
                            <div className="navbar__button-group">
                                {this.props.topicType === 'wire' ? <Dropdown
                                    label={gettext('Sort by:')}
                                    value={gettext('{{sort}}', {sort: this.state.sortValue})}
                                    className={'sorting-dropdown'}
                                    dropdownMenuHeader={gettext('Sort results by')}
                                >
                                    {
                                        this.sortValues.map((option) => (
                                            <button
                                                key={option.value}
                                                type='button'
                                                className='dropdown-item'
                                                onClick={() => {
                                                    option.sortFunction();
                                                    this.setState({sortValue: option.value});
                                                }}
                                            >
                                                {gettext(option.value)}
                                            </button>
                                        ))
                                    }
                                </Dropdown>: null}
                                <button
                                    className="nh-button nh-button--tertiary"
                                    onClick={() => {
                                        this.props.resetSearchParamsAndUpdateURL();
                                        this.props.onClearAll?.();
                                        this.props.refresh();
                                    }}
                                >
                                    {gettext('Clear All')}
                                </button>
                                <button
                                    data-test-id="toggle-search-bar"
                                    onClick={this.toggleTagSection}
                                    className="icon-button icon-button--tertiary icon-button--bordered"
                                >
                                    <i className={classNames(
                                        'icon--arrow-right',
                                        {
                                            'icon--collapsible-open': isTagSectionShown,
                                            'icon--collapsible-closed': !isTagSectionShown,
                                        }
                                    )} />
                                </button>
                            </div>
                        </div>
                    )}
                    {!isTagSectionShown ? null : (
                        <SearchResultTagsList
                            refresh={this.props.refresh}
                            user={this.props.user}
                            showSaveTopic={this.props.showSaveTopic}
                            saveMyTopic={this.props.saveMyTopic}
                            searchParams={this.props.searchParams}
                            activeTopic={this.props.activeTopic}
                            topicType={this.props.topicType}
                            navigations={this.props.navigations}
                            filterGroups={this.props.filterGroups}
                            availableFields={this.props.availableFields}
                            toggleNavigation={this.props.toggleNavigation}
                            toggleAdvancedSearchField={this.props.toggleAdvancedSearchField}
                            setQuery={this.props.setQuery}
                            setAdvancedSearchKeywords={this.props.setAdvancedSearchKeywords}
                            toggleFilter={this.props.toggleFilter}
                            setCreatedFilter={this.props.setCreatedFilter}
                            resetFilter={this.resetFilter}
                            clearAdvancedSearchParams={this.props.clearAdvancedSearchParams}
                            deselectMyTopic={this.props.deselectMyTopic}
                        />
                    )}

                    {this.props.children}
                </div>

                {!(this.props.newItems || []).length ? null : (
                    <div className="navbar navbar--flex navbar--small">
                        <div className="navbar__inner navbar__inner--end">
                            <NewItemsIcon
                                newItems={this.props.newItems}
                                refresh={this.props.refresh}
                            />
                        </div>
                    </div>
                )}
            </React.Fragment>
        );
    }
}

SearchResultsBarComponent.propTypes = {
    user: PropTypes.object,
    initiallyOpen: PropTypes.bool,

    minimizeSearchResults: PropTypes.bool,
    showTotalItems: PropTypes.bool,
    showTotalLabel: PropTypes.bool,
    showSaveTopic: PropTypes.bool,

    totalItems: PropTypes.number,
    totalItemsLabel: PropTypes.string,

    saveMyTopic: PropTypes.func,
    searchParams: PropTypes.object,
    activeTopic: PropTypes.object,
    topicType: PropTypes.string,

    newItems: PropTypes.array,
    refresh: PropTypes.func,

    navigations: PropTypes.object,
    filterGroups: PropTypes.object,
    availableFields: PropTypes.arrayOf(PropTypes.string).isRequired,

    toggleNavigation: PropTypes.func.isRequired,
    toggleAdvancedSearchField: PropTypes.func.isRequired,
    setQuery: PropTypes.func.isRequired,
    setAdvancedSearchKeywords: PropTypes.func.isRequired,
    toggleFilter: PropTypes.func.isRequired,
    setCreatedFilter: PropTypes.func.isRequired,
    resetSearchParamsAndUpdateURL: PropTypes.func.isRequired,
    clearAdvancedSearchParams: PropTypes.func.isRequired,
    deselectMyTopic: PropTypes.func.isRequired,
    resetFilter: PropTypes.func.isRequired,

    children: PropTypes.node,
};

SearchResultsBarComponent.defaultProps = {
    minimizeSearchResults: false,
    showTotalItems: true,
    showTotalLabel: true,
    showSaveTopic: false,
};

const mapStateToProps = (state: any) => ({
    user: state.userObject,
    searchParams: searchParamsSelector(state),
    navigations: navigationsByIdSelector(state),
    filterGroups: filterGroupsByIdSelector(state),
    availableFields: getAdvancedSearchFields(state.context),
});

const mapDispatchToProps = {
    toggleNavigation,
    toggleAdvancedSearchField,
    setAdvancedSearchKeywords,
    toggleFilter,
    setCreatedFilter,
    resetSearchParamsAndUpdateURL,
    clearAdvancedSearchParams,
    deselectMyTopic,
    resetFilter,
};

export const SearchResultsBar: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(SearchResultsBarComponent);
