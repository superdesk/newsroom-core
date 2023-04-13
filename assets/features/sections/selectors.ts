import {get} from 'lodash';

export const sectionsSelector = (state: any) => get(state, 'sections.list') || [];
export const activeSectionSelector = (state: any) => get(state, 'sections.active') || '';
export const uiSectionsSelector = (state: any) => sectionsSelector(state).filter(
    (section) => get(section, 'group') !== 'api'
);
