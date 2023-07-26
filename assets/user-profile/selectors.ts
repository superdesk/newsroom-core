import {get} from 'lodash';
import {DEFAULT_ENABLE_GLOBAL_TOPICS} from 'defaults';

const MENU_SECTION_MAPPING: any = {
    topics: 'wire',
    events: 'agenda',
    monitoring: 'monitoring',
};

export const userSelector = (state: any) => get(state, 'user');
export const selectedMenuSelector = (state: any) => get(state, 'selectedMenu');
export const selectedItemSelector = (state: any) => get(state, 'selectedItem');
export const displayModelSelector = (state: any) => get(state, 'displayModal');
export const userSectionsSelector = (state: any) => get(state, 'userSections');
export const topicEditorFullscreenSelector = (state: any) => get(state, 'editorFullscreen') || false;
export const sectionSelector = (state: any) => MENU_SECTION_MAPPING[state.selectedMenu];
export const foldersSelector = (state: any) => {
    const activeSection = sectionSelector(state);

    return state.folders.filter((folder: any) => folder.section === activeSection);
};

export const uiContextConfigSelector = (state: any, context: any) => get(state, `uiConfigs.${context}`) || {};
export const globalTopicsEnabledSelector = (state: any, context: any) => context === 'monitoring' ? false : get(
    state,
    `uiConfigs.${context}.enable_global_topics`,
    DEFAULT_ENABLE_GLOBAL_TOPICS
) === true && get(state, 'user.company.length') > 0;
