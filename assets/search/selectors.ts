import {createSelector} from 'reselect';
import {IAgendaState, ISearchParams} from 'interfaces';
import {get, find, filter as removeNulls, isEqual} from 'lodash';

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

export const searchParamsSelector = createSelector<
    IAgendaState,
    IAgendaState['search'],
    'wire' | 'agenda',
    ISearchParams
>(
    [(state) => state.search ?? {}, (state) => state.context],
    (search, context) => {
        const params: ISearchParams = {
            query: (search.activeQuery?.length ?? 0) ? search.activeQuery : undefined,
            sortQuery: (search.activeSortQuery?.length ?? 0) ? search.activeSortQuery : undefined,
            created: ((search.createdFilter?.from?.length ?? 0) + (search.createdFilter?.to?.length ?? 0)) > 0 ?
                search.createdFilter :
                undefined,
            navigation: search.activeNavigation ?? [],
            product: (search.productId?.length ?? 0) > 0 ? search.productId : undefined,
            topic_type: context,
        };

        if (
            search.advanced != null &&
            (search.advanced.all.length > 0 || search.advanced.any.length > 0 || search.advanced.exclude.length > 0)
        ) {
            params.advanced = {fields: search.advanced.fields};

            if (search.advanced.all.length > 0) {
                params.advanced.all = search.advanced.all;
            }
            if (search.advanced.any.length > 0) {
                params.advanced.any = search.advanced.any;
            }
            if (search.advanced.exclude.length > 0) {
                params.advanced.exclude = search.advanced.exclude;
            }
        }

        params.filter = {};
        for (const key of Object.keys(search.activeFilter || {})) {
            if (key === 'location') {
                params.filter[key] = search.activeFilter[key];
                continue;
            }

            const value = removeNulls(search.activeFilter[key]);

            if (value && value.length > 0) {
                params.filter[key] = value;
            }
        }

        if (Object.keys(params.filter).length === 0) {
            delete params.filter;
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
        return (
            (params.query?.length ?? 0) > 0 ||
            Object.keys(params.created ?? {}).filter((key) => params.created?.[key]).length > 0 ||
            Object.keys(params.filter ?? {}).filter((key) => params.filter?.[key]).length > 0 ||
            (params.advanced?.all?.length ?? 0) > 0 ||
            (params.advanced?.any?.length ?? 0) > 0 ||
            (params.advanced?.exclude?.length ?? 0) > 0
        );
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
