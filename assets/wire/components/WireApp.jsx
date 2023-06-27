import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {connect} from 'react-redux';
import {get, isEqual} from 'lodash';

import {gettext, getItemFromArray, DISPLAY_NEWS_ONLY, DISPLAY_ALL_VERSIONS_TOGGLE} from 'utils';
import {getSingleFilterValue} from 'search/utils';

import {
    fetchItems,
    fetchMoreItems,
    previewItem,
    toggleNews,
    toggleSearchAllVersions,
    downloadMedia,
} from 'wire/actions';

import {
    setView,
    setQuery,
    followStory,
    saveMyTopic,
} from 'search/actions';

import {
    searchQuerySelector,
    activeViewSelector,
    navigationsSelector,
    searchNavigationSelector,
    activeTopicSelector,
    activeProductSelector,
    searchFilterSelector,
    searchParamsSelector,
    showSaveTopicSelector,
    filterGroupsToLabelMap,
} from 'search/selectors';

import BaseApp from 'layout/components/BaseApp';
import WirePreview from './WirePreview';
import ItemsList from './ItemsList';
import SearchBar from 'search/components/SearchBar';
import SearchSidebar from './SearchSidebar';
import SelectedItemsBar from './SelectedItemsBar';
import ListViewControls from './ListViewControls';
import DownloadItemsModal from './DownloadItemsModal';
import ItemDetails from './ItemDetails';

import ShareItemModal from 'components/ShareItemModal';
import getItemActions from '../item-actions';
import BookmarkTabs from 'components/BookmarkTabs';
import ItemStatisticsModal from './ItemStatisticsModal';
import {AdvancedSearchPanel} from 'search/components/AdvancedSearchPanel';
import {SearchTipsPanel} from 'search/components/SearchTipsPanel';

import {SearchResultsBar} from 'search/components/SearchResultsBar';

import {
    previewConfigSelector,
    detailsConfigSelector,
    listConfigSelector,
    advancedSearchTabsConfigSelector,
} from 'ui/selectors';

const modals = {
    shareItem: ShareItemModal,
    downloadItems: DownloadItemsModal,
    itemStatistics: ItemStatisticsModal,
};

class WireApp extends BaseApp {
    constructor(props) {
        super(props);
        this.modals = modals;

        // Show my-topics tab only if WireApp is in 'wire' context (not 'aapX', etc.)
        this.tabs = this.tabs.filter((t) => get(this.props.advancedSearchTabConfig, t.id, true));
        if (this.props.context === 'monitoring') {
            let navTab = this.tabs.find((t) => t.id === 'nav');
            navTab.label = gettext('{{monitoring}} Profiles', sectionNames);
        }

        this.state.initialLoad = this.props.isLoading;

        this.toggleAdvancedSearchPanel = this.toggleAdvancedSearchPanel.bind(this);
        this.state.isAdvancedSearchShown = false;

        this.toggleSearchTipsPanel = this.toggleSearchTipsPanel.bind(this);
        this.state.isSearchTipsShown = false;
    }

    toggleAdvancedSearchPanel() {
        this.setState((prevState) => ({isAdvancedSearchShown: !prevState.isAdvancedSearchShown}));
    }

    toggleSearchTipsPanel() {
        this.setState((prevState) => ({isSearchTipsShown: !prevState.isSearchTipsShown}));
    }

    render() {
        if (this.state.initialLoad){
            return this.renderLoader();
        }

        return (
            <React.Fragment>
                <div className="content">
                    {this.renderPageContent()}
                </div>
                {!this.state.isAdvancedSearchShown ? null : (
                    <AdvancedSearchPanel
                        fetchItems={this.props.fetchItems}
                        toggleAdvancedSearchPanel={this.toggleAdvancedSearchPanel}
                        toggleSearchTipsPanel={this.toggleSearchTipsPanel}
                    />
                )}
                {!this.state.isSearchTipsShown ? null : (
                    <SearchTipsPanel
                        toggleSearchTipsPanel={this.toggleSearchTipsPanel}
                        defaultTab={this.state.isAdvancedSearchShown ? 'advanced' : 'regular'}
                    />
                )}
            </React.Fragment>
        );
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

        const newsOnlyFilterText = this.props.newsOnlyFilterText;
        const modal = this.renderModal(this.props.modal);

        const panesCount = [this.state.withSidebar, this.props.itemToPreview].filter((x) => x).length;
        const mainClassName = classNames('wire-column__main', {
            'wire-articles__one-side-pane': panesCount === 1,
            'wire-articles__two-side-panes': panesCount === 2,
        });

        const numNavigations = get(this.props, 'searchParams.navigation.length', 0);
        let showSaveTopic = this.props.context === 'wire' &&
            this.props.showSaveTopic &&
            !this.props.bookmarks;
        let showTotalItems = false;
        let showTotalLabel = false;
        let totalItemsLabel;
        const filterValue = getSingleFilterValue(this.props.activeFilter, ['genre', 'subject']);

        if (get(this.props, 'context') === 'wire') {
            if (get(this.props, 'activeTopic.label')) {
                totalItemsLabel = this.props.activeTopic.label;
                showTotalItems = showTotalLabel = true;
            } else if (numNavigations === 1) {
                totalItemsLabel = get(getItemFromArray(
                    this.props.searchParams.navigation[0],
                    this.props.navigations
                ), 'name') || '';
                showTotalItems = showTotalLabel = true;
            } else if (get(this.props, 'activeProduct.name')) {
                totalItemsLabel = this.props.activeProduct.name;
                showTotalItems = showTotalLabel = true;
            } else if (filterValue !== null) {
                totalItemsLabel = filterValue;
                showTotalItems = showTotalLabel = true;
            } else if (numNavigations > 1) {
                totalItemsLabel = gettext('Custom View');
                showTotalItems = showTotalLabel = true;
            } else if (this.props.showSaveTopic) {
                showTotalItems = showTotalLabel = true;
                if (this.props.bookmarks && get(this.props, 'searchParams.query.length', 0) > 0) {
                    totalItemsLabel = this.props.searchParams.query;
                }
            }
        } else {
            if (get(this.props, 'searchParams.query.length', 0) > 0) {
                totalItemsLabel = this.props.searchParams.query;
            }

            showTotalItems = showTotalLabel = !isEqual(
                this.props.searchParams,
                {navigation: [get(this.props, 'searchParams.navigation[0]')]}
            );
        }

        return (
            (this.props.itemToOpen ? [<ItemDetails key="itemDetails"
                item={this.props.itemToOpen}
                user={this.props.user}
                topics={this.props.topics}
                actions={this.filterActions(this.props.itemToOpen, this.props.previewConfig)}
                detailsConfig={this.props.detailsConfig}
                listConfig={this.props.listConfig}
                downloadMedia={this.props.downloadMedia}
                followStory={this.props.followStory}
                onClose={() => this.props.actions.filter(a => a.id === 'open')[0].action(null)}
                filterGroupLabels={this.props.filterGroupLabels}
            />] : [
                <section key="contentHeader" className='content-header'>
                    <h3 className="a11y-only">{gettext('{{wire}} Content', sectionNames)}</h3>
                    <SelectedItemsBar
                        actions={this.props.actions}
                    />
                    <nav className="content-bar navbar justify-content-start flex-nowrap flex-sm-wrap">
                        {this.state.withSidebar && <button
                            className='content-bar__menu content-bar__menu--nav--open'
                            ref={this.setOpenRef}
                            title={gettext('Close filter panel')}
                            aria-label={gettext('Close filter panel')}
                            onClick={this.toggleSidebar}>
                            <i className="icon--close-thin" />
                        </button>}

                        {this.props.bookmarks &&
                            <BookmarkTabs active={this.props.context} sections={this.props.userSections}/>
                        }

                        {!this.state.withSidebar && !this.props.bookmarks && <button
                            className="content-bar__menu content-bar__menu--nav"
                            ref={this.setCloseRef}
                            title={gettext('Open filter panel')}
                            aria-label={gettext('Open filter panel')}
                            onClick={this.toggleSidebar}>
                            <i className="icon--hamburger" />
                        </button>}

                        <SearchBar
                            fetchItems={this.props.fetchItems}
                            setQuery={this.props.setQuery}
                            toggleAdvancedSearchPanel={this.toggleAdvancedSearchPanel}
                            toggleSearchTipsPanel={this.toggleSearchTipsPanel}
                        />
                    </nav>
                </section>,
                <section key="contentMain" className='content-main'>
                    <div className='wire-column--3'>
                        <div className={`wire-column__nav ${this.state.withSidebar?'wire-column__nav--open':''}`}>
                            <h3 className="a11y-only">{gettext('Side filter panel')}</h3>
                            {this.state.withSidebar &&
                                <SearchSidebar tabs={this.tabs} props={{...this.props}} />
                            }
                        </div>
                        <div className={mainClassName}
                            ref={this.setListRef}
                        >
                            <SearchResultsBar
                                minimizeSearchResults={this.state.minimizeSearchResults}

                                showTotalItems={showTotalItems}
                                showTotalLabel={showTotalLabel}
                                showSaveTopic={showSaveTopic}

                                totalItems={this.props.totalItems}
                                totalItemsLabel={totalItemsLabel}

                                saveMyTopic={saveMyTopic}
                                activeTopic={this.props.activeTopic}
                                topicType={this.props.context === 'wire' ? this.props.context : null}

                                newItems={this.props.newItems}
                                refresh={this.props.fetchItems}

                                setQuery={this.props.setQuery}
                            >
                                <ListViewControls
                                    activeView={this.props.activeView}
                                    setView={this.props.setView}
                                    activeNavigation={this.props.activeNavigation}
                                    newsOnly={this.props.newsOnly}
                                    toggleNews={this.props.toggleNews}
                                    hideNewsOnly={!(this.props.context === 'wire' && DISPLAY_NEWS_ONLY && newsOnlyFilterText)}
                                    hideSearchAllVersions={!(this.props.context === 'wire' && DISPLAY_ALL_VERSIONS_TOGGLE)}
                                    searchAllVersions={this.props.searchAllVersions}
                                    toggleSearchAllVersions={this.props.toggleSearchAllVersions}
                                />
                            </SearchResultsBar>

                            <ItemsList
                                actions={this.props.actions}
                                activeView={this.props.activeView}
                                onScroll={this.onListScroll}
                            />
                        </div>

                        <div className={`wire-column__preview ${this.props.itemToPreview ? 'wire-column__preview--open' : ''}`}>
                            {this.props.itemToPreview &&
                            <WirePreview
                                item={this.props.itemToPreview}
                                user={this.props.user}
                                topics={this.props.topics}
                                actions={this.filterActions(this.props.itemToPreview, this.props.previewConfig)}
                                followStory={this.props.followStory}
                                closePreview={this.props.closePreview}
                                previewConfig={this.props.previewConfig}
                                downloadMedia={this.props.downloadMedia}
                                listConfig={this.props.listConfig}
                                filterGroupLabels={this.props.filterGroupLabels}
                            />
                            }

                        </div>
                    </div>
                </section>
            ]).concat([
                modal,
                this.renderNavBreadcrumb(
                    this.props.navigations,
                    this.props.activeNavigation,
                    this.props.activeTopic,
                    this.props.activeProduct,
                    this.props.activeFilter
                ),
                this.renderSavedItemsCount(),
            ])
        );
    }
}

WireApp.propTypes = {
    state: PropTypes.object,
    isLoading: PropTypes.bool,
    totalItems: PropTypes.number,
    activeQuery: PropTypes.string,
    itemToPreview: PropTypes.object,
    itemToOpen: PropTypes.object,
    itemsById: PropTypes.object,
    modal: PropTypes.object,
    user: PropTypes.string,
    company: PropTypes.string,
    topics: PropTypes.array,
    newsOnlyFilterText: PropTypes.string,
    fetchItems: PropTypes.func,
    actions: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string,
        action: PropTypes.func,
    })),
    setQuery: PropTypes.func.isRequired,
    bookmarks: PropTypes.bool,
    fetchMoreItems: PropTypes.func,
    activeView: PropTypes.string,
    setView: PropTypes.func,
    followStory: PropTypes.func,
    newItems: PropTypes.array,
    closePreview: PropTypes.func,
    navigations: PropTypes.array.isRequired,
    activeNavigation: PropTypes.arrayOf(PropTypes.string),
    toggleNews: PropTypes.func,
    newsOnly: PropTypes.bool,
    toggleSearchAllVersions: PropTypes.func,
    searchAllVersions: PropTypes.bool,
    activeTopic: PropTypes.object,
    activeProduct: PropTypes.object,
    activeFilter: PropTypes.object,
    savedItemsCount: PropTypes.number,
    userSections: PropTypes.object,
    context: PropTypes.string.isRequired,
    previewConfig: PropTypes.object,
    detailsConfig: PropTypes.object,
    listConfig: PropTypes.object,
    groups: PropTypes.array,
    downloadMedia: PropTypes.func,
    advancedSearchTabConfig: PropTypes.object,
    searchParams: PropTypes.object,
    showSaveTopic: PropTypes.bool,
    filterGroupLabels: PropTypes.object,
};

const mapStateToProps = (state) => ({
    state: state,
    isLoading: state.isLoading,
    newsOnlyFilterText: state.newsOnlyFilterText,
    totalItems: state.totalItems,
    activeQuery: searchQuerySelector(state),
    itemToPreview: state.previewItem ? state.itemsById[state.previewItem] : null,
    itemToOpen: state.openItem ? state.itemsById[state.openItem._id] : null,
    itemsById: state.itemsById,
    modal: state.modal,
    user: state.user,
    company: state.company,
    topics: state.topics || [],
    activeView: activeViewSelector(state),
    newItems: state.newItems,
    navigations: navigationsSelector(state),
    activeNavigation: searchNavigationSelector(state),
    newsOnly: !!get(state, 'wire.newsOnly'),
    searchAllVersions: !!get(state, 'wire.searchAllVersions'),
    bookmarks: state.bookmarks,
    savedItemsCount: state.savedItemsCount,
    userSections: state.userSections,
    activeTopic: activeTopicSelector(state),
    activeProduct: activeProductSelector(state),
    activeFilter: searchFilterSelector(state),
    context: state.context,
    previewConfig: previewConfigSelector(state),
    detailsConfig: detailsConfigSelector(state),
    listConfig: listConfigSelector(state),
    advancedSearchTabConfig: advancedSearchTabsConfigSelector(state),
    groups: get(state, 'groups', []),
    searchParams: searchParamsSelector(state),
    showSaveTopic: showSaveTopicSelector(state),
    filterGroupLabels: filterGroupsToLabelMap(state),
    errorMessage: state.errorMessage
});

const mapDispatchToProps = (dispatch) => ({
    followStory: (item) => followStory(item, 'wire'),
    fetchItems: () => dispatch(fetchItems()),
    toggleNews: () => {
        dispatch(toggleNews());
        dispatch(fetchItems());
    },
    toggleSearchAllVersions: () => {
        dispatch(toggleSearchAllVersions());
        dispatch(fetchItems());
    },
    setQuery: (query) => dispatch(setQuery(query)),
    actions: getItemActions(dispatch),
    fetchMoreItems: () => dispatch(fetchMoreItems()),
    setView: (view) => dispatch(setView(view)),
    closePreview: () => dispatch(previewItem(null)),
    downloadMedia: (href, id, mimeType) => dispatch(downloadMedia(href, id, mimeType)),
});

export default connect(mapStateToProps, mapDispatchToProps)(WireApp);
