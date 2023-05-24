import {NAVIGATIONS} from './navigations';

export const PRODUCTS = {
    wire: {
        all: {
            _id: '245460066f6a58e1c6b11540',
            name: 'All wire',
            query: 'slugline:wire',
            product_type: 'wire',
            is_enabled: true,
            navigations: [NAVIGATIONS.wire.all._id],
        },
        sports: {
            _id: '245460066f6a58e1c6b11541',
            name: 'Sports content',
            query: 'slugline:sports',
            product_type: 'wire',
            is_enabled: true,
            navigations: [NAVIGATIONS.wire.sports._id],
        },
    },
    agenda: {
        sports: {
            _id: '245460066f6a58e1c6b11542',
            name: 'Sports coverages',
            query: 'slugline:sports',
            product_type: 'agenda',
            is_enabled: true,
            navigations: [NAVIGATIONS.agenda.sports._id],
        },
    },
};
