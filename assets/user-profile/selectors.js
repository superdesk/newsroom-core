import {get} from 'lodash';
import {DEFAULT_ENABLE_GLOBAL_TOPICS} from 'defaults';

export const userSelector = (state) => get(state, 'user');
export const selectedMenuSelector = (state) => get(state, 'selectedMenu');
export const selectedItemSelector = (state) => get(state, 'selectedItem');
export const displayModelSelector = (state) => get(state, 'displayModal');
export const userSectionsSelector = (state) => get(state, 'userSections');
export const topicEditorFullscreenSelector = (state) => get(state, 'editorFullscreen') || false;
export const foldersSelector = (state) => {
    const sectionMapping = {
        topics: 'wire',
        events: 'agenda',
        monitoring: 'monitoring',
    };

    const activeSection = sectionMapping[state.selectedMenu];

    return state.folders.filter((folder) => folder.section === activeSection); 
};

export const uiContextConfigSelector = (state, context) => get(state, `uiConfigs.${context}`) || {};
export const globalTopicsEnabledSelector = (state, context) => context === 'monitoring' ? false : get(
    state,
    `uiConfigs.${context}.enable_global_topics`,
    DEFAULT_ENABLE_GLOBAL_TOPICS
) === true && get(state, 'user.company.length') > 0;
