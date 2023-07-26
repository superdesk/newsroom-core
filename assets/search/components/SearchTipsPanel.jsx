import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {gettext} from 'utils';
import {HTMLContent} from 'components/HTMLContent';

export class SearchTipsPanel extends React.Component {
    constructor(props) {
        super(props);

        this.state = {activeTab: this.props.defaultTab};
        this.handleTabClick = this.handleTabClick.bind(this);
    }

    handleTabClick(tabName) {
        this.setState({activeTab: tabName});
    }

    render() {
        const {toggleSearchTipsPanel} = this.props;
        const activeTabHtml = window.searchTipsHtml[this.state.activeTab] || '';

        if (activeTabHtml.length) {
            console.warn('Search tip HTML not found on window.');
        }

        return (
            <div className="advanced-search__wrapper">
                <div className="advanced-search__header">
                    <h3 className="a11y-only">{gettext('Advanced Search Tips dialog')}</h3>
                    <nav className="content-bar navbar">
                        <h3>{gettext('Tips')}</h3>
                        <div className="btn-group">
                            <div className="mx-2">
                                <button
                                    onClick={toggleSearchTipsPanel}
                                    className="icon-button icon-button icon-button--bordered"
                                    aria-label={gettext('Close Search Tips')}
                                >
                                    <i className="icon--close-thin" />
                                </button>
                            </div>
                        </div>
                    </nav>
                    <div className="advanced-search__subnav-wrapper">
                        <div className="advanced-search__subnav-content">
                            <ul className="nav nav-tabs nav-tabs--light">
                                <li className="nav-item">
                                    <a
                                        data-test-id="tab-regular"
                                        name="regular"
                                        className={classNames(
                                            'nav-link',
                                            {'active': this.state.activeTab === 'regular'}
                                        )}
                                        href="#"
                                        onClick={() => {
                                            this.handleTabClick('regular');
                                        }}
                                    >
                                        {gettext('Regular search')}
                                    </a>
                                </li>
                                <li className="nav-item">
                                    <a
                                        data-test-id="tab-advanced"
                                        name="advanced"
                                        className={classNames(
                                            'nav-link',
                                            {'active': this.state.activeTab === 'advanced'}
                                        )}
                                        href="#"
                                        onClick={() => {
                                            this.handleTabClick('advanced');
                                        }}
                                    >
                                        {gettext('Advanced search')}
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div className="advanced-search__content-wrapper">
                    <HTMLContent text={activeTabHtml} />
                </div>
            </div>
        );
    }
}

SearchTipsPanel.propTypes = {
    defaultTab: PropTypes.oneOf(['regular', 'advanced']),
    toggleSearchTipsPanel: PropTypes.func,
};

SearchTipsPanel.defaultProps = {
    defaultTab: 'regular',
};
