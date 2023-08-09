import {get} from 'lodash';
import {createSelector} from 'reselect';
import {getPicture} from './wire/utils';

export const formats = (state: any) => get(state, 'formats') || [];
export const secondaryFormats = (state: any) => get(state, 'secondaryFormats') || [];
export const context = (state: any) => get(state, 'context') || null;
export const allItemsById = (state: any) => get(state, 'itemsById') || null;
export const itemToOpen = (state: any) => get(state, 'itemToOpen') || null;
export const userSectionsSelector = (state: any) => get(state, 'userSections');
export const modalItems = (state: any) => get(state, 'modal.data.items') || [];

export const getFormats = createSelector([formats],(f) => (f.map((format: any) =>
    ({value: format.format, text: format.name}))));

export const getContextName = createSelector(
    [context, userSectionsSelector],
    (currentSection: any, sections: any) => get(sections, `${currentSection}.name`)
);

export const modalOptions: any = createSelector(
    [modalItems, formats, context, allItemsById, itemToOpen],
    (items: any, fmts: any, cntxt: any, itemsById: any, openItem: any) => {
        let options = fmts;
        if (items && items.length) {
            const itemType = cntxt === 'agenda' ? 'agenda' : 'wire';
            const hasPicture = items.every((itemId: any) => getPicture(itemsById && itemsById[itemId] || openItem));
            options = options.filter((opt: any) => get(opt, 'types', ['wire', 'agenda']).includes(itemType));
            if (!hasPicture) {
                options = options.filter((opt: any) => get(opt, 'assets', ['text']).includes('text'));
            }
        }

        return options.map((format: any) => ({value: format.format, text: format.name}));
    }
);

export const modalSecondaryFormatOptions = createSelector(
    [secondaryFormats], (fmts) => ( fmts.map((format: any) => ({value: format.format, text: format.name})) )
);
