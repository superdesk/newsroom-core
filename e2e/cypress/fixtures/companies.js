import {PRODUCTS} from './products';

export const COMPANIES = {
    sofab: {
        _id: '345460066f6a58e1c6b11540',
        name: 'Sourcefabric',
        is_enabled: true,
        sections: {wire: true, agenda: true},
        products: [
            {_id: PRODUCTS.wire.sports._id, section: PRODUCTS.wire.sports.product_type, seats: 2},
        ],
    },
    foobar: {
        _id: '345460066f6a58e1c6b11541',
        name: 'Foo Bar & Co',
        is_enabled: true,
        sections: {wire: true, agenda: true},
        products: [
            {_id: PRODUCTS.wire.all._id, section: PRODUCTS.wire.all.product_type, seats: 2},
            {_id: PRODUCTS.wire.sports._id, section: PRODUCTS.wire.sports.product_type, seats: 2},
            {_id: PRODUCTS.agenda.sports._id, section: PRODUCTS.agenda.sports.product_type, seats: 2},
        ],
    },
};
