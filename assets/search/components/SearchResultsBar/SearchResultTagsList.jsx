import * as React from 'react';
import PropTypes from 'prop-types';

import {SearchResultsTopicRow} from './SearchResultsTopicRow';
import {SearchResultsQueryRow} from './SearchResultsQueryRow';
import {SearchResultsAdvancedSearchRow} from './SearchResultsAdvancedSearchRow';
import {SearchResultsFiltersRow} from './SearchResultsFiltersRow';


export function SearchResultTagsList({
    user,
    showSaveTopic,
    showMyTopic,
    saveMyTopic,
    searchParams,
    activeTopic,
    topicType,
    navigations,
    filterGroups,
    availableFields,
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
            className="search-result__tags-list line-shadow-end--light"
        >
            <SearchResultsTopicRow
                user={user}
                searchParams={searchParams}
                activeTopic={activeTopic}
                navigations={navigations}
                showSaveTopic={showSaveTopic}
                showMyTopic={showMyTopic}
                topicType={topicType}
                saveMyTopic={saveMyTopic}
                toggleNavigation={toggleNavigation}
                deselectMyTopic={deselectMyTopic}
            />
            <SearchResultsQueryRow
                searchParams={searchParams}
                setQuery={setQuery}
            />
            <SearchResultsAdvancedSearchRow
                searchParams={searchParams}
                availableFields={availableFields}
                toggleAdvancedSearchField={toggleAdvancedSearchField}
                setAdvancedSearchKeywords={setAdvancedSearchKeywords}
                clearAdvancedSearchParams={clearAdvancedSearchParams}
            />
            <SearchResultsFiltersRow
                searchParams={searchParams}
                filterGroups={filterGroups}
                toggleFilter={toggleFilter}
                setCreatedFilter={setCreatedFilter}
                resetFilter={resetFilter}
            />
        </ul>
    );
}

SearchResultTagsList.propTypes = {
    user: PropTypes.object,
    showSaveTopic: PropTypes.bool,
    showMyTopic: PropTypes.bool,

    saveMyTopic: PropTypes.func,
    searchParams: PropTypes.object,
    activeTopic: PropTypes.object,
    topicType: PropTypes.string,

    navigations: PropTypes.object,
    filterGroups: PropTypes.object,
    availableFields: PropTypes.arrayOf(PropTypes.string).isRequired,

    toggleNavigation: PropTypes.func.isRequired,
    toggleAdvancedSearchField: PropTypes.func.isRequired,
    setQuery: PropTypes.func.isRequired,
    setAdvancedSearchKeywords: PropTypes.func.isRequired,
    toggleFilter: PropTypes.func.isRequired,
    setCreatedFilter: PropTypes.func.isRequired,
    clearAdvancedSearchParams: PropTypes.func.isRequired,

    deselectMyTopic: PropTypes.func,  // required if `showMyTopic === true`
    resetFilter: PropTypes.func.isRequired,
};

SearchResultTagsList.defaultProps = {
    showSaveTopic: false,
    showMyTopic: true,
};
