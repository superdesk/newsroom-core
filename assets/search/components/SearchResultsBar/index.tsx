import * as React from 'react';
import classNames from 'classnames';
import {connect} from 'react-redux';

import {IAgendaState, IFilterGroup, INavigation, ISearchFields, ISearchParams, ITopic, IUser, ISearchSortValue} from 'interfaces';

import {COLLAPSED_SEARCH_BY_DEFAULT, gettext} from 'utils';
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
    saveMyTopic,
} from '../../actions';

import {Dropdown} from './../../../components/Dropdown';

import {SearchResultTagsList} from './SearchResultTagsList';
import {IDateFilters} from 'interfaces/common';
import {ToolTip} from 'ui/components/ToolTip';
import {ICreatedFilter} from 'interfaces/search';
import {Popup} from 'ui/components/Popover';

interface ISortOption {
    label: string;
    value: ISearchSortValue;
}

interface IReduxStoreProps {
    user: IUser;
    searchParams: ISearchParams;
    navigations: {[key: string]: INavigation};
    filterGroups: {[key: string]: IFilterGroup};
    availableFields: ISearchFields;
}

interface IDispatchProps {
    toggleNavigation(navigation: INavigation): void;
    toggleAdvancedSearchField(field: string): void;
    setAdvancedSearchKeywords(field: string, keywords: string): void;
    toggleFilter(key: string, value: any, single: any): void;
    setCreatedFilter(createdFilter: ITopic['created']): void;
    resetSearchParamsAndUpdateURL(): void;
    clearAdvancedSearchParams(): void;
    deselectMyTopic?: (topicId: ITopic['_id']) => void;
    resetFilter(): void;
}

const defaultSortOptions: ISortOption[] = [
    {
        value: '', // versioncreated:desc is default
        label: gettext('Newest first'),
    },
    {
        value: 'versioncreated:asc',
        label: gettext('Oldest first'),
    },
    {
        value: '_score',
        label: gettext('Relevance'),
    },
];

interface IOwnProps {
    initiallyOpen?: boolean;
    minimizeSearchResults?: boolean;
    showTotalItems?: boolean;
    showTotalLabel?: boolean;
    showSaveTopic?: boolean;
    showSortDropdown?: boolean;
    showDefaultTimeframeLabel?: boolean;
    totalItems?: number;
    activeTopic: ITopic;
    topicType: ITopic['topic_type'];
    saveMyTopic?: (params: ISearchParams) => void;
    sortOptions?: ISortOption[];

    refresh(): void;
    onClearAll?(): void;
    setQuery(query: string): void;
    setSortQuery(query: ISearchSortValue): void;
    dateFilters?: IDateFilters;
    activeDateFilter?: ICreatedFilter;
}

type IProps = IReduxStoreProps & IDispatchProps & IOwnProps;

interface IState {
    isTagSectionShown: boolean;
}


class SearchResultsBarComponent extends React.Component<IProps, IState> {
    private topicNotNull: boolean;

    static defaultProps: Partial<IOwnProps> = {
        minimizeSearchResults: false,
        showTotalItems: true,
        showTotalLabel: true,
        showSaveTopic: false,
    };
    constructor(props: any) {
        super(props);

        this.topicNotNull = new URLSearchParams(window.location.search).get('topic') != null;

        this.state = {
            isTagSectionShown: COLLAPSED_SEARCH_BY_DEFAULT === true ? false : (this.props.initiallyOpen || this.topicNotNull),
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

    setSortQuery(sortQuery: ISearchSortValue) {
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

        const sortOptions = this.props.sortOptions || defaultSortOptions;
        const selectedSortOption = sortOptions.find((option) => option.value === (this.props.searchParams.sortQuery || ''));

        const defaultDateFilter = this.props.dateFilters?.find(dateFilter => dateFilter.default === true);

        return (
            <React.Fragment>
                <div
                    data-test-id="search-results-bar"
                    className="d-contents"
                >
                    {!this.props.showTotalItems ? null : (
                        <div className="navbar navbar--flex line-shadow-end--light navbar--search-results">
                            {!this.props.showTotalItems ? null : (
                                <div>
                                    <div className="search-result-count">
                                        {this.props.totalItems === 1 ?
                                            gettext('1 result') :
                                            gettext('{{ count }} results', {
                                                count: numberFormatter.format(this.props.totalItems || 0)
                                            })
                                        }
                                    </div>
                                    {this.props.showDefaultTimeframeLabel && (() => {
                                        if (!(this.props.activeDateFilter?.date_filter == null && defaultDateFilter?.name != null)) {
                                            return null;
                                        }
                                        const dateFilterName = defaultDateFilter.name;

                                        return (
                                            <span className='d-flex align-items-center'>
                                                <span className='popup-text--label'>{dateFilterName}</span>
    
                                                <Popup
                                                    placement='right'
                                                    component={({closePopup}) => (
                                                        <div className='p-1'>
                                                            <div className='d-flex justify-content-end'>
                                                                <button
                                                                    type="button"
                                                                    className="icon-button icon-button--secondary icon-button--small"
                                                                    aria-label={gettext('Close')}
                                                                    onClick={closePopup}
                                                                >
                                                                    <i className="icon--close-thin" />
                                                                </button>
                                                            </div>
                                                            <div className='pb-3 ps-3 pe-3'>
                                                                <p className='popup-text--info'>
                                                                    {gettext(
                                                                        'The initial search is limited to the {{dateFilterName}}. Please find different date ranges in the filter panel using the burger menu.',
                                                                        {dateFilterName: dateFilterName},
                                                                    )}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    )}
                                                >
                                                    {
                                                        (togglePopup) => (
                                                            <i
                                                                className="icon--info icon--info--smaller"
                                                                onClick={togglePopup}
                                                            />
                                                        )
                                                    }
                                                </Popup>
                                            </span>
                                        );
                                    })()}
                                </div>
                            )}
                            <div className="navbar__button-group">
                                {this.props.showSortDropdown !== true ? null : (
                                    <Dropdown
                                        label={gettext('Sort by:')}
                                        value={selectedSortOption?.label}
                                        className={'sorting-dropdown'}
                                        dropdownMenuHeader={gettext('Sort results by')}
                                    >
                                        {sortOptions.map((sortOption) => (
                                            <button
                                                key={sortOption.value}
                                                type="button"
                                                className="dropdown-item"
                                                onClick={() => {
                                                    this.setSortQuery(sortOption.value);
                                                }}
                                            >
                                                {sortOption.label}
                                            </button>
                                        ))}
                                    </Dropdown>
                                )}
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
                                <ToolTip key={`${isTagSectionShown}--state`} placement="left">
                                    <button
                                        title={
                                            isTagSectionShown
                                                ? gettext('Hide search terms')
                                                : gettext('Show search terms')
                                        }
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
                                </ToolTip>
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
                            toggleFilter={this.toggleFilter}
                            setCreatedFilter={this.setCreatedFilter}
                            resetFilter={this.resetFilter}
                            clearAdvancedSearchParams={this.props.clearAdvancedSearchParams}
                            deselectMyTopic={this.props.deselectMyTopic}
                            dateFilters={this.props.dateFilters}
                        />
                    )}

                    {this.props.children}
                </div>
            </React.Fragment>
        );
    }
}

const mapStateToProps = (state: IAgendaState) => ({
    user: state.userObject,
    searchParams: searchParamsSelector(state),
    navigations: navigationsByIdSelector(state),
    filterGroups: filterGroupsByIdSelector(state),
    availableFields: getAdvancedSearchFields(state.context),
    dateFilters: state.dateFilters,
    activeDateFilter: state.search.createdFilter
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
    saveMyTopic,
};

export const SearchResultsBar = connect<
    IReduxStoreProps,
    IDispatchProps,
    IOwnProps,
    IAgendaState
>(mapStateToProps, mapDispatchToProps)(SearchResultsBarComponent);
