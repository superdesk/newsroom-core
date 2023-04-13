import {uiConfigSelector} from 'assets/ui/selectors';
import {get} from 'lodash';

export const agendaFiltersConfigSelector = (state: any) => get(uiConfigSelector(state), 'subnav.filters') || [
    'item_type',
    'calendar',
    'location',
    'region',
    'coverage_type',
    'coverage_status',
];
