import * as React from 'react';
import PropTypes from 'prop-types';

import {SearchResultsTopicRow} from './SearchResultsTopicRow';
import {SearchResultsQueryRow} from './SearchResultsQueryRow';
import {SearchResultsAdvancedSearchRow} from './SearchResultsAdvancedSearchRow';
import {SearchResultsFiltersRow} from './SearchResultsFiltersRow';


export function SearchResultTagsList({
    user,
    showSaveTopic,
    saveMyTopic,
    searchParams,
    activeTopic,
    topicType,
    refresh,
    navigations,
    filterGroups,
    toggleNavigation,
    toggleAdvancedSearchField,
    setQuery,
    setAdvancedSearchKeywords,
    toggleFilter,
    setCreatedFilter,
    clearAdvancedSearchParams,
    deselectMyTopic,
    resetFilter,
}) {
    return (
        <ul
            data-test-id="search-result-tags"
            className="search-result__tags-list"
        >
            <SearchResultsTopicRow
                user={user}
                searchParams={searchParams}
                activeTopic={activeTopic}
                navigations={navigations}
                showSaveTopic={showSaveTopic}
                topicType={topicType}
                saveMyTopic={saveMyTopic}
                toggleNavigation={toggleNavigation}
                refresh={refresh}
                deselectMyTopic={deselectMyTopic}
            />
            <SearchResultsQueryRow
                searchParams={searchParams}
                setQuery={setQuery}
                refresh={refresh}
            />
            <SearchResultsAdvancedSearchRow
                searchParams={searchParams}
                toggleAdvancedSearchField={toggleAdvancedSearchField}
                setAdvancedSearchKeywords={setAdvancedSearchKeywords}
                refresh={refresh}
                clearAdvancedSearchParams={clearAdvancedSearchParams}
            />
            <SearchResultsFiltersRow
                searchParams={searchParams}
                filterGroups={filterGroups}
                toggleFilter={toggleFilter}
                setCreatedFilter={setCreatedFilter}
                resetFilter={resetFilter}
                refresh={refresh}
            />
        </ul>
    );
}

SearchResultTagsList.propTypes = {
    user: PropTypes.object,
    showSaveTopic: PropTypes.bool,

    saveMyTopic: PropTypes.func,
    searchParams: PropTypes.object,
    activeTopic: PropTypes.object,
    topicType: PropTypes.string,

    refresh: PropTypes.func,

    navigations: PropTypes.object,
    filterGroups: PropTypes.object,

    toggleNavigation: PropTypes.func.isRequired,
    toggleAdvancedSearchField: PropTypes.func.isRequired,
    setQuery: PropTypes.func.isRequired,
    setAdvancedSearchKeywords: PropTypes.func.isRequired,
    toggleFilter: PropTypes.func.isRequired,
    setCreatedFilter: PropTypes.func.isRequired,
    clearAdvancedSearchParams: PropTypes.func.isRequired,
    deselectMyTopic: PropTypes.func.isRequired,
    resetFilter: PropTypes.func.isRequired,
};

SearchResultTagsList.defaultProps = {
    showSaveTopic: false,
};
