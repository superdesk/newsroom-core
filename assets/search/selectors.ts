import {createSelector} from 'reselect';
import {get, find, filter as removeNulls, isEqual, isEmpty} from 'lodash';

export const searchQuerySelector = (state: any) => get(state, 'search.activeQuery') || null;
export const searchSortQuerySelector = (state: any) => get(state, 'search.activeSortQuery') || null;
export const searchFilterSelector = (state: any) => get(state, 'search.activeFilter');
export const searchCreatedSelector = (state: any) => get(state, 'search.createdFilter');
export const searchNavigationSelector = (state: any) => get(state, 'search.activeNavigation') || [];
export const searchTopicIdSelector = (state: any) => get(state, 'search.activeTopic') || null;
export const searchProductSelector = (state: any) => get(state, 'search.productId') || null;

const DEFAULT_ADVANCED_SEARCH_PARAMS = {
    all: '',
    any: '',
    exclude: '',
    fields: [],
};
export const advancedSearchParamsSelector = (state: any) => get(state, 'search.advanced') || DEFAULT_ADVANCED_SEARCH_PARAMS;

export const activeViewSelector = (state: any) => get(state, 'search.activeView');
export const navigationsSelector = (state: any) => get(state, 'search.navigations') || get(state, 'navigations') || [];

export const navigationsByIdSelector = createSelector(
    [navigationsSelector],
    (navigations) => navigations.reduce((navs: any, nav: any) => {
        navs[nav._id] = nav;

        return navs;
    }, {})
);

export const topicsSelector = (state: any) => get(state, 'topics') || [];
export const productsSelector = (state: any) => get(state, 'search.products') || [];

export const filterGroups = (state: any) => get(state, 'groups') || [];
export const filterGroupsByIdSelector = createSelector(
    [filterGroups],
    (listOfGroups) => listOfGroups.reduce((groups: any, group: any) => {
        groups[group.field] = group;

        return groups;
    }, {})
);

export const activeTopicSelector = createSelector(
    [searchTopicIdSelector, topicsSelector],
    (topicId: any, topics: any) => find(topics, {'_id': topicId})
);

export const activeProductSelector = createSelector(
    [searchProductSelector, productsSelector],
    (productId: any, products: any) => find(products, {'_id': productId})
);

export const resultsFilteredSelector = (state: any) => state.resultsFiltered;

export const searchParamsSelector = createSelector(
    [searchQuerySelector, searchSortQuerySelector, searchCreatedSelector, searchNavigationSelector, searchFilterSelector, searchProductSelector, advancedSearchParamsSelector],
    (query: any, sortQuery: any, created: any, navigation: any, filter: any, product: any, advancedSearchParams: any) => {
        const params: any = {};

        if (!isEmpty(query)) {
            params.query = query;
        }

        if (!isEmpty(sortQuery)) {
            params.sortQuery = sortQuery;
        }

        if (!isEmpty(created)) {
            params.created = created;
        }

        if (!isEmpty(navigation)) {
            params.navigation = navigation;
        }

        if (product) {
            params.product = product;
        }

        if (advancedSearchParams.all || advancedSearchParams.any || advancedSearchParams.exclude) {
            params.advanced = {fields: advancedSearchParams.fields};

            if (advancedSearchParams.all) {
                params.advanced.all = advancedSearchParams.all;
            }
            if (advancedSearchParams.any) {
                params.advanced.any = advancedSearchParams.any;
            }
            if (advancedSearchParams.exclude) {
                params.advanced.exclude = advancedSearchParams.exclude;
            }
        }

        if (filter && Object.keys(filter).length > 0) {
            params.filter = {};
            Object.keys(filter).forEach((key: any) => {
                if (key === 'location') {
                    params.filter[key] = filter[key];
                    return;
                }

                const value = removeNulls(filter[key]);

                if (value && value.length > 0) {
                    params.filter[key] = value;
                }
            });

            if (isEmpty(params.filter)) {
                delete params.filter;
            }
        }

        return params;
    }
);

export const showSaveTopicSelector = createSelector(
    [searchParamsSelector, activeTopicSelector],
    (current: any, topic: any) => {
        const areTopicFieldsSame = (field1: any, filed2: any) => {
            if (field1 && filed2) {
                return isEqual(field1, filed2);
            }

            if (!field1 && !filed2) {
                return true;
            }

            return false;
        };

        if (!topic) {
            if (isEqual(current, {})) {
                return false;
            }

            // If there is only a single navigation selected, then don't enable the 'SAVE' button
            return !(
                isEqual(Object.keys(current), ['navigation']) &&
                get(current, 'navigation.length', 0) === 1
            );
        } else if (!areTopicFieldsSame(get(current, 'query'), get(topic, 'query'))) {
            return true;
        } else if (!areTopicFieldsSame(get(current, 'created'), get(topic, 'created'))) {
            return true;
        } else if (!areTopicFieldsSame(get(current, 'filter'), get(topic, 'filter'))) {
            return true;
        } else if(!areTopicFieldsSame(get(current, 'advanced'), get(topic, 'advanced'))) {
            return true;
        }

        return !isEqual(
            (get(current, 'navigation') || []).sort(),
            (get(topic, 'navigation') || []).sort()
        );
    }
);

export const isSearchFiltered = createSelector(
    [searchParamsSelector],
    (params: any) => {
        return get(params, 'query', '').length > 0 ||
            Object.keys(get(params, 'created', {})).filter((key: any) => get(params.created, key)).length > 0 ||
            Object.keys(get(params, 'filter', {})).filter((key: any) => get(params.filter, key)).length > 0;
    }
);

export const filterGroupsToLabelMap = createSelector(
    [filterGroups],
    (groups: any) => (
        groups.reduce(
            (groupMap: any, group: any) => {
                groupMap[group.field] = group.label;

                return groupMap;
            },
            {}
        )
    )
);
