import {get} from 'lodash';
import {uiConfigSelector} from 'ui/selectors';

export const agendaFiltersConfigSelector = (state) => get(uiConfigSelector(state), 'subnav.filters') || [
    'item_type',
    'calendar',
    'location',
    'region',
    'coverage_type',
    'coverage_status',
];
