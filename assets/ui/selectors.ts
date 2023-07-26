import {get} from 'lodash';
import {DEFAULT_ENABLE_GLOBAL_TOPICS} from 'defaults';

const EMPTY_OBJECT = {};

export const uiConfigSelector = (state: any) => get(state, 'uiConfig') || EMPTY_OBJECT;
export const previewConfigSelector = (state: any) => uiConfigSelector(state).preview || EMPTY_OBJECT;
export const detailsConfigSelector = (state: any) => uiConfigSelector(state).details || EMPTY_OBJECT;
export const listConfigSelector = (state: any) => uiConfigSelector(state).list || EMPTY_OBJECT;
export const advancedSearchTabsConfigSelector = (state: any) => uiConfigSelector(state).advanced_search_tabs || EMPTY_OBJECT;
export const multiSelectTopicsConfigSelector = (state: any) => uiConfigSelector(state).multi_select_topics || false;
export const companiesSubscriberIdEnabled = (state: any) => get(state, 'ui_config.list.sd_subscriber_id.enabled', false);
export const isSearchEnabled = (state: any) => uiConfigSelector(state).search || false;
export const agendaContentLinkTarget = (state: any) => uiConfigSelector(state).open_coverage_content_in_same_page === true ?
    '_self' :
    '_blank';

export const globalTopicsEnabledSelector = (state: any) => get(
    uiConfigSelector(state),
    'enable_global_topics',
    DEFAULT_ENABLE_GLOBAL_TOPICS
) === true;
