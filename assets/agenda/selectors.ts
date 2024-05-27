import {IAgendaState} from 'interfaces/agenda';
import {AgendaFilterTypes} from 'interfaces/configs';

export const agendaFiltersConfigSelector = (state: IAgendaState): AgendaFilterTypes[] => (state.uiConfig.subnav?.filters || [
    'item_type',
    'calendar',
    'location',
    'region',
    'coverage_type',
    'coverage_status',
]);

export const agendaSubnavItemTypeConfigSelector = (state: IAgendaState) => (state.uiConfig.subnav?.item_type || {});
