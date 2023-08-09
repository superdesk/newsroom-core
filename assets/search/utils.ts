import {get} from 'lodash';
import {getConfig} from 'utils';

export const noNavigationSelected = (activeNavigation: any) => (
    get(activeNavigation, 'length', 0) < 1
);

export const getNavigationUrlParam = (activeNavigation: any, ignoreEmpty: any = true, useJSON: any = true) => {
    if (!ignoreEmpty && noNavigationSelected(activeNavigation)) {
        return null;
    }

    return useJSON ?
        JSON.stringify(activeNavigation) :
        (activeNavigation || []).join(',');
};

export const getSearchParams = (custom: any, topic: any) => {
    const params: any = {};

    ['query', 'created', 'navigation', 'filter', 'product', 'advanced'].forEach(
        (field: any) => {
            if (get(custom, field)) {
                params[field] = custom[field];
            } else if (get(topic, field)) {
                params[field] = topic[field];
            }
        }
    );

    return params;
};

export const getSingleFilterValue = (activeFilter: any, fields: any) => {
    const filterKeys = Object.keys(activeFilter || {});

    if (filterKeys.length !== 1 || !fields.includes(filterKeys[0])) {
        return null;
    } else if (activeFilter[filterKeys[0]].length === 1) {
        return activeFilter[filterKeys[0]][0];
    }

    return null;
};

export function getAdvancedSearchFields(context: any) {
    const config = getConfig('advanced_search', {
        fields: {
            wire: ['headline', 'slugline', 'body_html'],
            agenda: ['name', 'headline', 'slugline', 'description'],
        },
    });

    return (config.fields || {})[context];
}
