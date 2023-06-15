import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {searchParamsSelector, navigationsByIdSelector, filterGroupsByIdSelector} from '../../selectors';
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

import {SearchResultsTopicRow} from './SearchResultsTopicRow';
import {SearchResultsQueryRow} from './SearchResultsQueryRow';
import {SearchResultsAdvancedSearchRow} from './SearchResultsAdvancedSearchRow';
import {SearchResultsFiltersRow} from './SearchResultsFiltersRow';


class SearchResultsBarComponent extends React.Component {
    constructor(props) {
        super(props);

        this.state = {isTagSectionShown: false};
        this.toggleTagSection = this.toggleTagSection.bind(this);
    }

    toggleTagSection() {
        this.setState((prevState) => ({isTagSectionShown: !prevState.isTagSectionShown}));
    }

    render() {
        const {isTagSectionShown} = this.state;
        const numberFormat = (new Intl.NumberFormat(window.locale || 'en', {style: 'decimal'}));

        return (
            <div className="wire-column__main-header-container">
                {!this.props.showTotalItems ? null : (
                    <div className="navbar navbar--flex line-shadow-end--light">
                        {!this.props.showTotalItems ? null : (
                            <div className="search-result-count">
                                {this.props.totalItems === 1 ?
                                    gettext('1 result') :
                                    gettext('{{ count }} results', {
                                        count: numberFormat.format(this.props.totalItems || 0)
                                    })
                                }
                            </div>
                        )}
                        <div className="navbar__button-group">
                            <button
                                className="btn btn-outline-secondary"
                                onClick={() => {
                                    this.props.resetSearchParamsAndUpdateURL();
                                    this.toggleTagSection();
                                    this.props.refresh();
                                }}
                            >
                                {gettext('Clear all')}
                            </button>
                            <button
                                onClick={this.toggleTagSection}
                                className="icon-button icon-button--bordered"
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
                    <div className="navbar navbar--flex line-shadow-end--light navbar--auto-height">
                        <ul className="search-result__tags-list">
                            <SearchResultsTopicRow
                                user={this.props.user}
                                searchParams={this.props.searchParams}
                                activeTopic={this.props.activeTopic}
                                navigations={this.props.navigations}
                                showSaveTopic={this.props.showSaveTopic}
                                topicType={this.props.topicType}
                                saveMyTopic={this.props.saveMyTopic}
                                toggleNavigation={this.props.toggleNavigation}
                                refresh={this.props.refresh}
                                deselectMyTopic={this.props.deselectMyTopic}
                            />
                            <SearchResultsQueryRow
                                searchParams={this.props.searchParams}
                                setQuery={this.props.setQuery}
                                refresh={this.props.refresh}
                            />
                            <SearchResultsAdvancedSearchRow
                                searchParams={this.props.searchParams}
                                toggleAdvancedSearchField={this.props.toggleAdvancedSearchField}
                                setAdvancedSearchKeywords={this.props.setAdvancedSearchKeywords}
                                refresh={this.props.refresh}
                                clearAdvancedSearchParams={this.props.clearAdvancedSearchParams}
                            />
                            <SearchResultsFiltersRow
                                searchParams={this.props.searchParams}
                                filterGroups={this.props.filterGroups}
                                toggleFilter={this.props.toggleFilter}
                                setCreatedFilter={this.props.setCreatedFilter}
                                resetFilter={this.props.resetFilter}
                                refresh={this.props.refresh}
                            />
                        </ul>
                    </div>
                )}

                {this.props.children}
            </div>
        );
    }
}

SearchResultsBarComponent.propTypes = {
    user: PropTypes.object,

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

const mapStateToProps = (state) => ({
    user: state.userObject,
    searchParams: searchParamsSelector(state),
    navigations: navigationsByIdSelector(state),
    filterGroups: filterGroupsByIdSelector(state),
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

export const SearchResultsBar = connect(mapStateToProps, mapDispatchToProps)(SearchResultsBarComponent);
