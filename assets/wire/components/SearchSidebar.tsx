import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {setActiveFilterTab, getActiveFilterTab} from 'local-store';
import {gettext} from 'utils';

class SearchSidebar extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any) {
        super(props);
        const activeTabId = getActiveFilterTab(props.props.context);

        this.state = {
            active: props.tabs.findIndex((tab: any) => tab.id === activeTabId) >= 0 ?
                activeTabId :
                props.tabs[0].id
        };
    }

    selectTab(tabId: string) {
        setActiveFilterTab(tabId, this.props.props.context);
        this.setState({active: tabId});
    }

    onTabKeyDown(event: React.KeyboardEvent, index: number) {
        const tabs = this.props.tabs;
        let next: number;

        switch (event.key) {
        case 'ArrowRight':
            next = (index + 1) % tabs.length;
            break;
        case 'ArrowLeft':
            next = (index - 1 + tabs.length) % tabs.length;
            break;
        case 'Home':
            next = 0;
            break;
        case 'End':
            next = tabs.length - 1;
            break;
        default:
            return;
        }

        event.preventDefault();
        this.selectTab(tabs[next].id);
        document.getElementById(`filter-tab--${tabs[next].id}`)?.focus();
    }

    render() {
        return (
            <div className='wire-column__nav__items'>
                <ul className='nav' id='pills-tab' role='tablist' aria-label={gettext('Filter panel')}>
                    {this.props.tabs.map((tab: any, index: number) => (
                        <li
                            className='wire-column__nav__tab nav-item'
                            key={tab.id}
                            role='presentation'
                            data-test-id={`filter-panel-tab--${tab.id}`}
                        >
                            <a className={`nav-link ${this.state.active === tab.id && 'active'}`}
                                role='tab'
                                id={`filter-tab--${tab.id}`}
                                aria-selected={`${this.state.active === tab.id ? 'true' : 'false'}`}
                                aria-controls={`filter-tabpanel--${tab.id}`}
                                tabIndex={this.state.active === tab.id ? 0 : -1}
                                href=''
                                onKeyDown={(event) => this.onTabKeyDown(event, index)}
                                onClick={(event: any) => {
                                    event.preventDefault();
                                    this.selectTab(tab.id);
                                }}>{tab.label}</a>
                        </li>
                    ))}
                </ul>
                {this.props.tabs.map((tab: any) => (
                    <div
                        className="tab-content"
                        key={tab.id}
                        data-test-id={`filter-panel-content--${tab.id}`}
                    >
                        <div
                            className={classNames('tab-pane tab-pane--no-padding', 'fade', {'show active': this.state.active === tab.id})}
                            role='tabpanel'
                            id={`filter-tabpanel--${tab.id}`}
                            aria-labelledby={`filter-tab--${tab.id}`}
                            data-test-id={this.state.active === tab.id ? 'tab-panel-content--active' : undefined}
                        >
                            <tab.component {...this.props.props} />
                        </div>
                    </div>
                ))}
            </div>
        );
    }
}

SearchSidebar.propTypes = {
    tabs: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string.isRequired,
        label: PropTypes.string.isRequired,
        component: PropTypes.func.isRequired,
    })),
    props: PropTypes.object,
};

export default SearchSidebar;
