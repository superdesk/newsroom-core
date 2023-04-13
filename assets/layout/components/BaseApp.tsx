import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {createPortal} from 'react-dom';
import {Tooltip} from 'bootstrap';
import {getFilterPanelOpenState, setFilterPanelOpenState} from 'assets/local-store';
import TopicsTab from 'assets/search/components/TopicsTab';
import {getSingleFilterValue} from 'assets/search/utils';
import {isMobilePhone, gettext, isDisplayed, isTouchDevice} from 'assets/utils';
import FiltersTab from 'assets/wire/components/filters/FiltersTab';
import NavigationTab from 'assets/wire/components/filters/NavigationTab';

export default class BaseApp extends React.Component<any, any> {
    dom: any;
    tooltips: any;
    tabs: any;
    modals: any;
    static propTypes: any;
    constructor(props: any) {
        super(props);

        this.state = {
            withSidebar: props.bookmarks !== true && getFilterPanelOpenState(props.context),
            minimizeSearchResults: isMobilePhone(),
            initialLoad: props.isLoading,
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

    renderModal(specs: any) {
        if (specs) {
            const Modal = this.modals[specs.modal];
            return (
                <Modal key="modal" data={specs.data} />
            );
        }
    }

    renderNavBreadcrumb(navigations: any, activeNavigation: any, activeTopic: any, activeProduct: any = null, activeFilter = null) {
        const dest = document.getElementById('nav-breadcrumb');
        if (!dest) {
            return null;
        }

        let name;
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
        if (container !== this.dom.list && !this.dom.list?.contains(container)) {
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

    filterActions(item: any, config: any, includeCoverages=false) {
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

    getSnapshotBeforeUpdate() {
        this.disposeTooltips();
        return null;
    }

    componentDidUpdate(nextProps: any) {
        if ((nextProps.activeQuery || this.props.activeQuery) && (nextProps.activeQuery !== this.props.activeQuery) && this.dom.list != null) {
            this.dom.list.scrollTop = 0;
        }
        this.initTooltips();
    }
}

BaseApp.propTypes = {
    state: PropTypes.object.isRequired,
    context: PropTypes.string.isRequired,
    actions: PropTypes.arrayOf(PropTypes.object).isRequired,
    activeQuery: PropTypes.string,
    fetchMoreItems: PropTypes.func.isRequired,
    savedItemsCount: PropTypes.number,
    bookmarks: PropTypes.bool,
    isLoading: PropTypes.bool,
};
