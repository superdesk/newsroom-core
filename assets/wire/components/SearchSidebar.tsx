import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {setActiveFilterTab, getActiveFilterTab} from 'local-store';

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

    render() {
        return (
            <div className='wire-column__nav__items'>
                <ul className='nav' id='pills-tab' role='tablist'>
                    {this.props.tabs.map((tab: any) => (
                        <li
                            className='wire-column__nav__tab nav-item'
                            key={tab.id}
                            data-test-id={`filter-panel-tab--${tab.id}`}
                        >
                            <a className={`nav-link ${this.state.active === tab.id && 'active'}`}
                                role='tab'
                                aria-selected={`${this.state.active === tab.id ? 'true' : 'false'}`}
                                aria-label={tab.label}
                                href=''
                                onClick={(event: any) => {
                                    event.preventDefault();
                                    setActiveFilterTab(tab.id, this.props.props.context);
                                    this.setState({active: tab.id});
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
