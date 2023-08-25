import * as React from 'react';

import {SearchResultsTopicRow} from './SearchResultsTopicRow';
import {SearchResultsQueryRow} from './SearchResultsQueryRow';
import {SearchResultsAdvancedSearchRow} from './SearchResultsAdvancedSearchRow';
import {SearchResultsFiltersRow} from './SearchResultsFiltersRow';
import {IFilterGroup, INavigation, ISearchFields, ISearchParams, ITopic, IUser} from 'interfaces';
import {SearchResultTagList} from './SearchResultTagList';
import {gettext} from 'utils';

export interface IProps {
    user: IUser;
    showMyTopic?: boolean;
    showSaveTopic?: boolean;
    readonly?: boolean;

    searchParams: ISearchParams;
    activeTopic: ITopic;
    topicType: ITopic['topic_type'];
    navigations: {[key: string]: INavigation};
    filterGroups: {[key: string]: IFilterGroup};
    availableFields: ISearchFields;

    setQuery(): void;
    resetFilter(): void;
    refresh?(): void;
    toggleNavigation(navigation: INavigation): void;
    toggleAdvancedSearchField(field: string): void;
    setAdvancedSearchKeywords(field: string, keywords: string): void;
    clearAdvancedSearchParams(): void;
    toggleFilter(key: string, value: any, single: any): void;
    setCreatedFilter(createdFilter: ITopic['created']): void;

    saveMyTopic?: (params: ISearchParams) => void;
    deselectMyTopic?: (topicId: ITopic['_id']) => void;
}

export function SearchResultTagsList({
    user,
    showSaveTopic = false,
    showMyTopic = true,
    readonly = false,
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
    refresh,
}: IProps) {
    return (
        <ul
            data-test-id="search-result-tags"
            className="search-result__tags-list line-shadow-end--light"
        >
            <SearchResultsTopicRow
                user={user}
                readonly={readonly}
                searchParams={searchParams}
                activeTopic={activeTopic}
                navigations={navigations}
                showSaveTopic={showSaveTopic === true}
                showMyTopic={showMyTopic === true}
                topicType={topicType}
                saveMyTopic={saveMyTopic}
                toggleNavigation={toggleNavigation}
                deselectMyTopic={deselectMyTopic}
            />
            <SearchResultsQueryRow
                searchParams={searchParams}
                setQuery={setQuery}
                readonly={readonly}
            />
            <SearchResultsAdvancedSearchRow
                searchParams={searchParams}
                availableFields={availableFields}
                refresh={refresh}
                toggleAdvancedSearchField={toggleAdvancedSearchField}
                setAdvancedSearchKeywords={setAdvancedSearchKeywords}
                clearAdvancedSearchParams={clearAdvancedSearchParams}
                readonly={readonly}
            />
            <SearchResultsFiltersRow
                searchParams={searchParams}
                filterGroups={filterGroups}
                toggleFilter={toggleFilter}
                setCreatedFilter={setCreatedFilter}
                resetFilter={resetFilter}
                readonly={readonly}
            />
            {readonly === true && activeTopic._id && (
                <SearchResultTagList
                    testId="search-results--edit-button"
                    tags={[
                        (
                            <a
                                key="tag-filters--edit-button"
                                className='nh-button nh-button--tertiary nh-button--small'
                                href={`/${topicType}?topic=${activeTopic._id}`}
                            >
                                {gettext('Edit search terms')}
                            </a>
                        ),
                    ]}
                />
            )}
        </ul>
    );
}
