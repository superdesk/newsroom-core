import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {toggleNavigation, toggleFilter, setCreatedFilter} from 'search/actions';
import {removeNewItems} from 'wire/actions';
import {loadMyWireTopic} from 'wire/actions';
import {loadMyAgendaTopic} from 'agenda/actions';
import {
    activeTopicSelector,
    navigationsByIdSelector,
    searchParamsSelector,
    searchParamTagSelector,
} from 'search/selectors';
import {Tag} from 'components/Tag';

class ContentSearchResultsComponent extends React.Component {
    constructor(props) {
        super(props);

        this.state = {expanded: false};
        this.toggleExpanded = this.toggleExpanded.bind(this);
    }

    componentDidUpdate(prevProps) {
        if (prevProps.minimizeSearchResults && !this.props.minimizeSearchResults) {
            this.setState({expanded: false});
        }
    }

    toggleExpanded() {
        this.setState({expanded: !this.state.expanded});
    }

    getTagsToRender() {
        if (this.props.minimizeSearchResults) {
            if (this.state.expanded) {
                return this.props.searchParamTags;
            } else {
                return this.props.searchParamTags.filter((tag) => (
                    ['navigation', 'topic'].includes(tag.type)
                ));
            }
        }

        return this.props.searchParamTags;
    }

    renderTags() {
        const searchParamTags = this.getTagsToRender();

        return searchParamTags.map((tag) => (
            <Tag
                key={tag.key}
                keyValue={tag.key}
                label={tag.label}
                text={tag.text}
                shade={tag.shade}
                onClick={() => {
                    if (tag.type === 'navigation') {
                        this.props.toggleNavigation(tag.params, this.props.disableSameNavigationDeselect);
                        this.props.fetchItems();
                    } else if (tag.type === 'topic') {
                        // toggle topic
                        if (tag.params.topic_type === 'agenda') {
                            this.props.loadMyAgendaTopic(tag.params._id);
                        } else {
                            this.props.loadMyWireTopic(tag.params._id);
                        }
                    } else if (tag.type === 'filter') {
                        // toggle filter
                        this.props.toggleFilter(tag.params.group.field, tag.params.value, tag.params.group.single);
                        this.props.fetchItems();
                    } else if (tag.type === 'created') {
                        // toggle created
                        const params = {...tag.params};

                        switch (tag.key) {
                        case 'published_relative':
                            // Remove `from` and `to`
                            params.from = null;
                            params.to = null;
                            break;
                        case 'published_from':
                            // Remove `from`
                            params.from = null;
                            break;
                        case 'published_to':
                            // Remove 'to`
                            params.to = null;
                            break;
                        }

                        this.props.setCreatedFilter(params);
                        this.props.fetchItems();
                    }
                }}
            />
        ));
    }

    render() {
        if (!this.props.showTotalItems && !this.props.showSaveTopic && !this.props.children) {
            return null;
        }

        return (
            <div className={classNames(
                'wire-column__main-header px-1 px-md-3',
                {
                    'wire-column__main-header--expanded': this.props.minimizeSearchResults && this.state.expanded,
                    'wire-column__main-header--small': this.props.minimizeSearchResults,
                }
            )}>
                <div className="d-flex flex-column flex-md-row">
                    <div className="d-flex flex-column justify-content-center w-100">
                        <div className="navbar-text search-results-info">
                            {!this.props.showTotalItems ? null : (
                                <span className="search-results-info__num">
                                    {this.props.totalItems}
                                </span>
                            )}
                            {!this.props.showTotalLabel ? null : (
                                <React.Fragment>
                                    <span className="search-results-info__text flex-column">
                                        <span>{gettext('search results for: ') +' '+this.props.searchParams.query}</span>
                                    </span>
                                    {!(this.props.minimizeSearchResults && !this.state.expanded) ? null : (
                                        <div
                                            data-test-id="search-result-tags"
                                            className="tags-list"
                                        >
                                            {this.renderTags()}
                                        </div>
                                    )}
                                </React.Fragment>
                            )}
                            {!this.props.showSaveTopic && !this.props.children ? null : (
                                <div className="d-flex ms-auto align-items-center">
                                    {this.props.showSaveTopic && (
                                        <div
                                            data-test-id="save-topic-btn"
                                            className="d-none d-md-flex align-items-center flex-shrink-0 ml-auto"
                                        >
                                            <button
                                                className="btn btn-outline-primary btn-sm d-none d-sm-block mb-1 mt-1"
                                                onClick={this.props.saveMyTopic}
                                            >{this.props.saveButtonText}</button>
                                        </div>
                                    )}
                                    {(this.props.showSaveTopic || this.props.children) && (
                                        <div className="d-flex ms-auto align-items-end align-items-md-center flex-column flex-md-row flex-shrink-0">
                                            <button
                                                className="btn btn-outline-primary btn-sm d-block d-sm-none mb-1 mt-1"
                                                onClick={this.props.saveMyTopic}
                                            >{this.props.saveButtonText}</button>
                                            {this.props.children}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                        {(this.props.minimizeSearchResults && !this.state.expanded) ? null : (
                            <div
                                data-test-id="search-result-tags"
                                className="tags-list"
                            >
                                {this.renderTags()}
                            </div>
                        )}
                    </div>
                </div>
                {!this.props.minimizeSearchResults ? null : (
                    <div className="search-results__toggle">
                        <button
                            className={classNames(
                                'search-results__toggle-button',
                                {active: this.state.expanded}
                            )}
                            onClick={this.toggleExpanded}
                        >
                            <i className="icon--arrow-right" />
                        </button>
                    </div>
                )}
            </div>
        );
    }
}

ContentSearchResultsComponent.propTypes = {
    minimizeSearchResults: PropTypes.bool,
    showTotalItems: PropTypes.bool,
    showTotalLabel: PropTypes.bool,
    showSaveTopic: PropTypes.bool,

    totalItems: PropTypes.number,
    totalItemsLabel: PropTypes.string,
    saveMyTopic: PropTypes.func,
    saveButtonText: PropTypes.string,
    disableSameNavigationDeselect: PropTypes.bool,
    fetchItems: PropTypes.func.isRequired,
    children: PropTypes.node,

    // Redux Props
    searchParams: PropTypes.object,
    searchParamTags: PropTypes.array,
    navigations: PropTypes.object,
    currentTopic: PropTypes.object,
    toggleNavigation: PropTypes.func,
    toggleFilter: PropTypes.func,
    setCreatedFilter: PropTypes.func,
    removeNewItems: PropTypes.func,
    loadMyWireTopic: PropTypes.func,
    loadMyAgendaTopic: PropTypes.func,
};

const mapStateToProps = (state: any) => ({
    navigations: navigationsByIdSelector(state),
    searchParams: searchParamsSelector(state),
    searchParamTags: searchParamTagSelector(state),
    currentTopic: activeTopicSelector(state),
});

const mapDispatchToProps = {
    toggleNavigation,
    toggleFilter,
    setCreatedFilter,
    removeNewItems,
    loadMyWireTopic,
    loadMyAgendaTopic,
};

export const ContentSearchResults = connect(
    mapStateToProps,
    mapDispatchToProps
)(ContentSearchResultsComponent);
