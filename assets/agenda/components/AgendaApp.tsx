import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {connect} from 'react-redux';
import {get, isEmpty} from 'lodash';

import {ISearchSortValue} from 'interfaces';
import {gettext} from 'utils';
import {noNavigationSelected, searchParamsUpdated} from 'search/utils';

import {
    fetchItems,
    selectDate,
    fetchMoreItems,
    previewItem,
    toggleDropdownFilter,
    openItemDetails,
    requestCoverage,
    toggleFeaturedFilter,
} from 'agenda/actions';

import {
    setView,
    setQuery,
    saveMyTopic,
    setSortQuery,
} from 'search/actions';

import {
    searchQuerySelector,
    activeViewSelector,
    searchFilterSelector,
    searchCreatedSelector,
    searchNavigationSelector,
    navigationsSelector,
    topicsSelector,
    activeTopicSelector,
    searchParamsSelector,
    showSaveTopicSelector,
} from 'search/selectors';

import SearchBase from 'layout/components/SearchBase';
import AgendaPreview from './AgendaPreview';
import AgendaList from './AgendaList';
import SearchBar from 'search/components/SearchBar';
import SearchSidebar from 'wire/components/SearchSidebar';
import SelectedItemsBar from 'wire/components/SelectedItemsBar';
import AgendaListViewControls from './AgendaListViewControls';
import DownloadItemsModal from 'wire/components/DownloadItemsModal';
import AgendaItemDetails from 'agenda/components/AgendaItemDetails';

import ShareItemModal from 'components/ShareItemModal';
import {getAgendaItemActions, getCoverageItemActions} from '../item-actions';
import AgendaFilters from './AgendaFilters';
import AgendaDateNavigation from './AgendaDateNavigation';
import BookmarkTabs from 'components/BookmarkTabs';
import {setActiveDate, setAgendaDropdownFilter} from 'local-store';
import {previewConfigSelector, detailsConfigSelector} from 'ui/selectors';
import {SearchResultsBar} from 'search/components/SearchResultsBar';
import NewItemsIcon from 'search/components/NewItemsIcon';

const modals = {
    shareItem: ShareItemModal,
    downloadItems: DownloadItemsModal,
};

class AgendaApp extends SearchBase<any> {
    static propTypes: any;

    modals: any;
    tabs: any;

    constructor(props: any) {
        super(props);
        this.modals = modals;

        this.fetchItemsOnNavigation = this.fetchItemsOnNavigation.bind(this);
    }

    getTabs() {
        return this.props.featuredOnly ?  this.tabs.filter((t: any) => t.id !== 'filters') : this.tabs;
    }


    fetchItemsOnNavigation() {
        // Toggle featured filter to 'false'
        if (this.props.featuredOnly) {
            this.props.toggleFeaturedFilter(false);
        }


        this.props.fetchItems();
    }

    renderPageContent() {
        if (this.props.errorMessage) {
            return (
                <div className="wire-articles__item-wrap col-12">
                    <div className="alert alert-secondary">
                        {this.props.errorMessage}
                    </div>
                </div>
            );
        }

        const modal = this.renderModal(this.props.modal);
        const showDatePicker = isEmpty(this.props.createdFilter.from) && isEmpty(this.props.createdFilter.to) && !this.props.bookmarks;

        const panesCount = [this.state.withSidebar, this.props.itemToPreview].filter((x: any) => x).length;
        const mainClassName = classNames('wire-column__main', {
            'wire-articles__one-side-pane': panesCount === 1,
            'wire-articles__two-side-panes': panesCount === 2,
        });

        const onDetailClose = this.props.detail ? null :
            () => this.props.actions.filter((a: any) => a.id === 'open')[0].action(null, this.props.previewGroup, this.props.previewPlan);
        const eventsOnly = this.props.itemTypeFilter === 'events' || this.props.eventsOnlyAccess;
        const hideFeaturedToggle = !noNavigationSelected(this.props.activeNavigation) ||
            this.props.bookmarks ||
            this.props.activeTopic ||
            eventsOnly;

        const numNavigations = get(this.props, 'searchParams.navigation.length', 0);
        const showSaveTopic = this.props.showSaveTopic &&
            !this.props.bookmarks &&
            !this.props.featuredOnly;
        let showTotalItems = false;
        let showTotalLabel = false;

        if (get(this.props, 'activeTopic.label')) {
            showTotalItems = showTotalLabel = true;
        } else if (numNavigations === 1) {
            showTotalItems = showTotalLabel = true;
        } else if (numNavigations > 1) {
            showTotalItems = showTotalLabel = true;
        } else if (this.props.showSaveTopic) {
            showTotalItems = showTotalLabel = true;
        }

        const showFilters = searchParamsUpdated(this.props.searchParams) ||
            this.props.activeTopic != null ||
            Object.keys(this.props.activeFilter ?? {}).length > 0 ||
            this.props.activeQuery != null ||
            this.props.itemTypeFilter != null;

        return (
            (this.props.itemToOpen ? [<AgendaItemDetails key="itemDetails"
                item={this.props.itemToOpen}
                user={this.props.user}
                actions={this.filterActions(this.props.itemToOpen, this.props.previewConfig, true)}
                onClose={onDetailClose}
                requestCoverage={this.props.requestCoverage}
                group={this.props.previewGroup}
                planningId={this.props.previewPlan}
                eventsOnly={eventsOnly}
                coverageActions={this.props.coverageActions}
                detailsConfig={this.props.detailsConfig}
                restrictCoverageInfo={this.props.restrictCoverageInfo}
            />] : [
                <section key="contentHeader" className='content-header'>
                    <h3 className="a11y-only">{gettext('{{agenda}} Content', window.sectionNames)}</h3>
                    <SelectedItemsBar
                        actions={this.props.actions}
                    />
                    <nav className="content-bar navbar justify-content-start flex-nowrap">
                        {this.state.withSidebar && (
                            <button
                                className="content-bar__menu content-bar__menu--nav--open"
                                ref={this.setOpenRef}
                                title={gettext('Close filter panel')}
                                aria-label={gettext('Close filter panel')}
                                onClick={this.toggleSidebar}
                            >
                                <i className="icon--close-thin" />
                            </button>
                        )}

                        {!this.state.withSidebar && !this.props.bookmarks && (
                            <button
                                className="content-bar__menu content-bar__menu--nav"
                                ref={this.setCloseRef}
                                title={gettext('Open filter panel')}
                                aria-label={gettext('Open filter panel')}
                                onClick={this.toggleSidebar}
                            >
                                <i className="icon--hamburger" />
                            </button>
                        )}

                        {this.props.bookmarks && (
                            <BookmarkTabs active="agenda" sections={this.props.userSections}/>
                        )}

                        <SearchBar
                            fetchItems={this.props.fetchItems}
                            setQuery={this.props.setQuery}
                            toggleAdvancedSearchPanel={this.toggleAdvancedSearchPanel}
                            toggleSearchTipsPanel={this.toggleSearchTipsPanel}
                        />

                        {showDatePicker && (
                            <AgendaDateNavigation
                                selectDate={this.props.selectDate}
                                activeDate={this.props.activeDate}
                                createdFilter={this.props.createdFilter}
                                activeGrouping={this.props.activeGrouping}
                                displayCalendar={true}
                            />
                        )}
                    </nav>
                </section>,
                <section key="contentMain" className='content-main'>
                    <div className={`wire-column--3 ${this.state.withSidebar?'nav--open':''}`}>
                        <div className={`wire-column__nav ${this.state.withSidebar?'wire-column__nav--open':''}`}>
                            <h3 className="a11y-only">{gettext('Side filter panel')}</h3>
                            {this.state.withSidebar && (
                                <SearchSidebar
                                    tabs={this.getTabs()}
                                    props={{
                                        ...this.props,
                                        fetchItems: this.fetchItemsOnNavigation}}
                                />
                            )}
                        </div>
                        <div className={mainClassName}>
                            <div className='wire-column__main-header-container'>
                                {!this.props.bookmarks && (
                                    <AgendaFilters
                                        toggleFilter={this.props.toggleDropdownFilter}
                                        activeFilter={this.props.activeFilter}
                                        eventsOnlyAccess={this.props.eventsOnlyAccess}
                                        restrictCoverageInfo={this.props.restrictCoverageInfo}
                                        itemTypeFilter={this.props.itemTypeFilter}
                                    />
                                )}
                                {
                                    showFilters && (
                                        <SearchResultsBar
                                            initiallyOpen={showFilters}
                                            minimizeSearchResults={this.state.minimizeSearchResults}
                                            showTotalItems={showTotalItems}
                                            showTotalLabel={showTotalLabel}
                                            showSaveTopic={showSaveTopic}
                                            onClearAll={() => {
                                                this.props.toggleDropdownFilter('itemType', null);
                                            }}
                                            totalItems={this.props.totalItems}
                                            saveMyTopic={saveMyTopic}
                                            activeTopic={this.props.activeTopic}
                                            topicType="agenda"
                                            refresh={this.props.fetchItems}
                                            setQuery={this.props.setQuery}
                                            setSortQuery={this.props.setSortQuery}
                                            showSortDropdown={true}
                                            sortOptions={[
                                                {label: gettext('Date'), value: ''},
                                                {label: gettext('Newest updates'), value: 'versioncreated:desc'},
                                                {label: gettext('Oldest updates'), value: 'versioncreated:asc'},
                                                {label: gettext('Relevance'), value: '_score'},
                                            ]}
                                        />
                                    )
                                }
                                <AgendaListViewControls
                                    activeView={this.props.activeView}
                                    setView={this.props.setView}
                                    hideFeaturedToggle={!!hideFeaturedToggle}
                                    toggleFeaturedFilter={this.props.toggleFeaturedFilter}
                                    featuredFilter={this.props.featuredOnly}
                                    hasAgendaFeaturedItems={this.props.hasAgendaFeaturedItems}
                                />
                                {!(this.props.newItems || []).length ? null : (
                                    <div className="navbar navbar--flex navbar--small">
                                        <div className="navbar__inner navbar__inner--end">
                                            <NewItemsIcon
                                                newItems={this.props.newItems}
                                                refresh={this.props.fetchItems}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>
                            <AgendaList
                                actions={this.props.actions}
                                activeView={this.props.activeView}
                                onScroll={this.onListScroll}
                                refNode={this.setListRef}
                            />
                        </div>

                        <AgendaPreview
                            item={this.props.itemToPreview}
                            user={this.props.user}
                            actions={this.filterActions(this.props.itemToPreview, this.props.previewConfig, true)}
                            coverageActions={this.props.coverageActions}
                            closePreview={this.props.closePreview}
                            openItemDetails={this.props.openItemDetails}
                            requestCoverage={this.props.requestCoverage}
                            previewGroup={this.props.previewGroup}
                            previewPlan={this.props.previewPlan}
                            eventsOnly={eventsOnly}
                            previewConfig={this.props.previewConfig}
                            restrictCoverageInfo={this.props.restrictCoverageInfo}
                        />
                    </div>
                </section>
            ] as any).concat([
                modal,
                this.renderNavBreadcrumb(
                    this.props.navigations,
                    this.props.activeNavigation,
                    this.props.activeTopic
                ),
                this.renderSavedItemsCount(),
            ])
        );
    }
}

AgendaApp.propTypes = {
    state: PropTypes.object,
    isLoading: PropTypes.bool,
    totalItems: PropTypes.number,
    hasAgendaFeaturedItems: PropTypes.bool,
    activeQuery: PropTypes.string,
    activeFilter: PropTypes.object,
    createdFilter: PropTypes.object,
    itemToPreview: PropTypes.object,
    previewGroup: PropTypes.string,
    previewPlan: PropTypes.string,
    itemToOpen: PropTypes.object,
    itemsById: PropTypes.object,
    modal: PropTypes.object,
    user: PropTypes.string,
    company: PropTypes.string,
    topics: PropTypes.array,
    fetchItems: PropTypes.func,
    actions: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string,
        action: PropTypes.func,
    })),
    bookmarks: PropTypes.bool,
    fetchMoreItems: PropTypes.func,
    activeView: PropTypes.string,
    setView: PropTypes.func,
    newItems: PropTypes.array,
    closePreview: PropTypes.func,
    navigations: PropTypes.array.isRequired,
    activeNavigation: PropTypes.arrayOf(PropTypes.string),
    toggleDropdownFilter: PropTypes.func,
    selectDate: PropTypes.func,
    activeDate: PropTypes.number,
    activeGrouping: PropTypes.string,
    activeTopic: PropTypes.object,
    openItemDetails: PropTypes.func,
    requestCoverage: PropTypes.func,
    detail: PropTypes.bool,
    savedItemsCount: PropTypes.number,
    userSections: PropTypes.object,
    context: PropTypes.string,
    eventsOnlyAccess: PropTypes.bool,
    restrictCoverageInfo: PropTypes.bool,
    itemTypeFilter: PropTypes.string,
    searchParams: PropTypes.object,
    showSaveTopic: PropTypes.bool,
    previewConfig: PropTypes.object,
    detailsConfig: PropTypes.object,
    groups: PropTypes.array,
    dateFilters: PropTypes.array,
};

const mapStateToProps = (state: any) => ({
    state: state,
    isLoading: state.isLoading,
    totalItems: state.totalItems,
    activeQuery: searchQuerySelector(state),
    activeFilter: searchFilterSelector(state),
    createdFilter: searchCreatedSelector(state),
    itemToPreview: state.previewItem ? state.itemsById[state.previewItem] : null,
    previewGroup: state.previewGroup,
    previewPlan: state.previewPlan,
    itemToOpen: state.openItem ? state.itemsById[state.openItem._id] : null,
    itemsById: state.itemsById,
    modal: state.modal,
    user: state.user,
    company: state.company,
    topics: topicsSelector(state),
    activeView: activeViewSelector(state),
    newItems: state.newItems,
    navigations: navigationsSelector(state),
    activeTopic: activeTopicSelector(state),
    activeNavigation: searchNavigationSelector(state),
    bookmarks: state.bookmarks,
    activeDate: get(state, 'agenda.activeDate'),
    activeGrouping: get(state, 'agenda.activeGrouping'),
    eventsOnlyAccess: get(state, 'agenda.eventsOnlyAccess', false),
    restrictCoverageInfo: get(state, 'agenda.restrictCoverageInfo', false),
    itemTypeFilter: get(state, 'agenda.itemType'),
    detail: get(state, 'detail', false),
    savedItemsCount: state.savedItemsCount,
    userSections: state.userSections,
    featuredOnly: get(state, 'agenda.featuredOnly'),
    context: state.context,
    setQuery: PropTypes.func.isRequired,
    searchParams: searchParamsSelector(state),
    showSaveTopic: showSaveTopicSelector(state),
    previewConfig: previewConfigSelector(state),
    detailsConfig: detailsConfigSelector(state),
    groups: get(state, 'groups', []),
    hasAgendaFeaturedItems: state.hasAgendaFeaturedItems,
    errorMessage: state.errorMessage,
    dateFilters: state.dateFilters,
});

const mapDispatchToProps = (dispatch: any) => ({
    fetchItems: () => dispatch(fetchItems()),
    actions: getAgendaItemActions(dispatch),
    coverageActions: getCoverageItemActions(dispatch),
    fetchMoreItems: () => dispatch(fetchMoreItems()),
    setView: (view: any) => dispatch(setView(view)),
    closePreview: () => dispatch(previewItem(null)),
    toggleDropdownFilter: (field: any, value: any) => {
        setAgendaDropdownFilter(field, value);
        dispatch(toggleDropdownFilter(field, value));
    },
    selectDate: (dateString: any, grouping: any) => {
        dispatch(selectDate(dateString, grouping));
        setActiveDate(dateString);
        dispatch(fetchItems());
    },
    openItemDetails: (item: any) => dispatch(openItemDetails(item)),
    requestCoverage: (item: any, message: any) => dispatch(requestCoverage(item, message)),
    toggleFeaturedFilter: (fetch: any) => dispatch(toggleFeaturedFilter(fetch)),
    setQuery: (query: any) => dispatch(setQuery(query)),
    setSortQuery: (query: ISearchSortValue) => dispatch(setSortQuery(query)),
});

const component: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(AgendaApp);

export default component;
