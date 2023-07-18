import {get} from 'lodash';
import {DEFAULT_ENABLE_GLOBAL_TOPICS} from 'defaults';

const EMPTY_OBJECT = {};

export const uiConfigSelector = (state) => get(state, 'uiConfig') || EMPTY_OBJECT;
export const previewConfigSelector = (state) => uiConfigSelector(state).preview || EMPTY_OBJECT;
export const detailsConfigSelector = (state) => uiConfigSelector(state).details || EMPTY_OBJECT;
export const listConfigSelector = (state) => uiConfigSelector(state).list || EMPTY_OBJECT;
export const advancedSearchTabsConfigSelector = (state) => uiConfigSelector(state).advanced_search_tabs || EMPTY_OBJECT;
export const multiSelectTopicsConfigSelector = (state) => uiConfigSelector(state).multi_select_topics || false;
export const companiesSubscriberIdEnabled = (state) => get(state, 'ui_config.list.sd_subscriber_id.enabled', false);
export const isSearchEnabled = (state) => uiConfigSelector(state).search || false;
export const agendaContentLinkTarget = (state) => uiConfigSelector(state).open_coverage_content_in_same_page === true ?
    '_self' :
    '_blank';

export const globalTopicsEnabledSelector = (state) => get(
    uiConfigSelector(state),
    'enable_global_topics',
    DEFAULT_ENABLE_GLOBAL_TOPICS
) === true;
