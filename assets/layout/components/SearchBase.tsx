import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {createPortal} from 'react-dom';
import {Tooltip} from 'bootstrap';

import {IArticle, IAgendaItem, IListConfig, IPreviewConfig, IItemAction} from 'interfaces';
import {isTouchDevice, gettext, isDisplayed, isMobilePhone} from 'utils';
import {getSingleFilterValue} from 'search/utils';
import {getFilterPanelOpenState, setFilterPanelOpenState} from 'local-store';

// tabs
import TopicsTab from 'search/components/TopicsTab';
import FiltersTab from 'wire/components/filters/FiltersTab';
import NavigationTab from 'wire/components/filters/NavigationTab';
import {AdvancedSearchPanel} from 'search/components/AdvancedSearchPanel';
import {SearchTipsPanel} from 'search/components/SearchTipsPanel';

interface IBaseState {
    withSidebar: boolean;
    minimizeSearchResults: boolean;
    initialLoad: boolean;
    isAdvancedSearchShown: boolean;
    isSearchTipsShown: boolean;
}

interface IBaseProps {
    bookmarks: any;
    savedItemsCount: number;
    context: any;
    actions: any;
    fetchMoreItems: () => Promise<void>;
    state: any;
    fetchItems: () => Promise<void>;
    activeQuery: any;
}

export default class SearchBase<Props = {}> extends React.Component<Props & IBaseProps, IBaseState & any> {
    static propTypes: any;
    dom: any;
    tooltips: any;
    tabs: any;
    modals: any;
    constructor(props: any) {
        super(props);

        this.state = {
            withSidebar: props.bookmarks !== true && getFilterPanelOpenState(props.context),
            minimizeSearchResults: isMobilePhone(),
            initialLoad: props.isLoading,
            isAdvancedSearchShown: false,
            isSearchTipsShown: false,
        };

        this.dom = {
            open: null,
            close: null,
            list: null,
        };
        this.tooltips = {
            open: null,
            close: null,
        };

        this.toggleSidebar = this.toggleSidebar.bind(this);
        this.onListScroll = this.onListScroll.bind(this);
        this.filterActions = this.filterActions.bind(this);
        this.setOpenRef = this.setOpenRef.bind(this);
        this.setCloseRef = this.setCloseRef.bind(this);
        this.setListRef = this.setListRef.bind(this);
        this.toggleAdvancedSearchPanel = this.toggleAdvancedSearchPanel.bind(this);
        this.toggleSearchTipsPanel = this.toggleSearchTipsPanel.bind(this);

        this.tabs = [
            {id: 'nav', label: gettext('Topics'), component: NavigationTab},
            {id: 'topics', label: gettext('My Topics'), component: TopicsTab},
            {id: 'filters', label: gettext('Filters'), component: FiltersTab},
        ];
    }

    static getDerivedStateFromProps(props: any) {
        if (props.isLoading === false) {
            return {initialLoad: false};
        }

        return null;
    }

    setOpenRef(elem: any) {
        this.dom.open = elem;
    }

    setCloseRef(elem: any) {
        this.dom.close = elem;
    }

    setListRef(elem: any) {
        this.dom.list = elem;
    }

    toggleAdvancedSearchPanel() {
        this.setState((prevState: any) => ({isAdvancedSearchShown: !prevState.isAdvancedSearchShown}));
    }

    toggleSearchTipsPanel() {
        this.setState((prevState: any) => ({isSearchTipsShown: !prevState.isSearchTipsShown}));
    }

    renderModal(specs: any) {
        if (specs) {
            const Modal = this.modals[specs.modal];
            return (
                <Modal key="modal" data={specs.data} />
            );
        }
    }

    renderNavBreadcrumb(navigations: any, activeNavigation: any, activeTopic: any, activeProduct: any = null, activeFilter: any = null) {
        const dest = document.getElementById('nav-breadcrumb');
        if (!dest) {
            return null;
        }

        let name: any;
        const numNavigations = get(activeNavigation, 'length', 0);
        const filterValue = getSingleFilterValue(activeFilter, ['genre', 'subject']);

        if (activeTopic) {
            name = `/ ${activeTopic.label}`;
        } else if (numNavigations > 1) {
            name = '/ ' + gettext('Custom View');
        } else if (numNavigations === 1) {
            name = '/ ' + get(navigations.find((nav: any) => nav._id === activeNavigation[0]), 'name', '');
        } else if (activeProduct != null) {
            name = `/ ${activeProduct.name}`;
        } else if (filterValue !== null) {
            name = `/ ${filterValue}`;
        } else {
            name = '';
        }

        return createPortal(name , dest);
    }

    renderSavedItemsCount() {
        const dest = document.getElementById('saved-items-count');
        if (!dest) {
            return null;
        }

        return createPortal(this.props.savedItemsCount, dest);
    }

    renderLoader() {
        return (
            <div className="d-flex justify-content-center h-50">
                <div className="spinner-border text-muted m-5 align-self-center" />
            </div>
        );
    }

    toggleSidebar(event: any) {
        event.preventDefault();
        this.setState({withSidebar: !this.state.withSidebar});
        setFilterPanelOpenState(!this.state.withSidebar, this.props.context);
    }

    onListScroll(event: any) {
        const BUFFER = 10;
        const container = event.target;

        // this probably won't happen with react 17 but keeping it for now
        if (container !== this.dom.list && !this.dom.list.contains(container)) {
            // Not scrolled on the actual list
            return;
        }

        if (container.scrollTop + container.offsetHeight + BUFFER >= container.scrollHeight) {
            this.props.fetchMoreItems()
                .catch(() => null); // ignore
        }

        if(container.scrollTop > BUFFER) {
            this.setState({
                minimizeSearchResults: true,
            });
        }
        else {
            this.setState({
                minimizeSearchResults: isMobilePhone(),
            });
        }
    }

    filterActions(
        item?: IArticle | IAgendaItem,
        config?: IListConfig | IPreviewConfig,
        includeCoverages = false
    ): Array<IItemAction> {
        if (item == null) {
            return [];
        }

        return this.props.actions.filter((action: any) => (!config || isDisplayed(action.id, config)) &&
          (!action.when || action.when(this.props.state, item, includeCoverages)));
    }

    componentDidMount() {
        this.initTooltips();

        document.dispatchEvent(new Event('newshub-core--app-rendered'));
    }

    initTooltips() {
        if (!isTouchDevice()) {
            if (this.dom.open) {
                this.tooltips.open = new Tooltip(this.dom.open);
            }
            if (this.dom.close) {
                this.tooltips.close = new Tooltip(this.dom.close);
            }
        }
    }

    disposeTooltips() {
        if (this.dom.open && this.tooltips.open) {
            this.tooltips.open.dispose();
        }
        if (this.dom.close && this.tooltips.close) {
            this.tooltips.close.dispose();
        }
    }

    componentWillUnmount() {
        this.disposeTooltips();
    }

    getSnapshotBeforeUpdate(prevProps: any) {
        this.disposeTooltips();
        return null;
    }

    componentDidUpdate(nextProps: any) {
        if ((nextProps.activeQuery || this.props.activeQuery) && (nextProps.activeQuery !== this.props.activeQuery) && this.dom.list != null) {
            this.dom.list.scrollTop = 0;
        }
        this.initTooltips();
    }

    renderPageContent() {
        return <div/>;
    }

    render() {
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
}

SearchBase.propTypes = {
    state: PropTypes.object.isRequired,
    context: PropTypes.string.isRequired,
    actions: PropTypes.arrayOf(PropTypes.object).isRequired,
    activeQuery: PropTypes.string,
    fetchMoreItems: PropTypes.func.isRequired,
    fetchItems: PropTypes.func.isRequired,
    savedItemsCount: PropTypes.number,
    bookmarks: PropTypes.bool,
    isLoading: PropTypes.bool,
};
