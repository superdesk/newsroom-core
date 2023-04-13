
export const INIT_SECTIONS = 'INIT_SECTIONS';
export function initSections(sections: any): any {
    return {type: INIT_SECTIONS, sections: sections};
}

export const SELECT_SECTION = 'SELECT_SECTION';
export function selectSection(section: any): any {
    return {type: SELECT_SECTION, section: section};
}
