import {COMPANIES} from './companies';
import {PRODUCTS} from './products';

export const USERS = {
    none: {
        admin: {
            // Created by backend, see `/api/e2e/init` endpoint
            _id: '445460066f6a58e1c6b11540',
            first_name: 'Admin',
            last_name: 'Nistrator',
            email: 'admin@nistrator.org',
            password: '$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG',
            user_type: 'administrator',
            is_validated: true,
            is_enabled: true,
            is_approved: true,
            sections: {wire: true, agenda: true},
            products: [],
        },
    },
    foobar: {
        admin: {
            _id: '445460066f6a58e1c6b11541',
            company: COMPANIES.foobar._id,
            first_name: 'Foo',
            last_name: 'Bar',
            email: 'foo@bar.com',
            password: '$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG',
            user_type: 'company_admin',
            is_validated: true,
            is_enabled: true,
            is_approved: true,
            sections: {wire: true, agenda: true},
            products: [
                {_id: PRODUCTS.wire.all._id, section: PRODUCTS.wire.all.product_type},
                {_id: PRODUCTS.wire.sports._id, section: PRODUCTS.wire.sports.product_type},
                {_id: PRODUCTS.agenda.sports._id, section: PRODUCTS.agenda.sports.product_type},
            ],
        },
        monkey: {
            _id: '445460066f6a58e1c6b11542',
            company: COMPANIES.foobar._id,
            first_name: 'Monkey',
            last_name: 'Mania',
            email: 'monkey.mania@bar.com',
            password: '$2b$12$HGyWCf9VNfnVAwc2wQxQW.Op3Ejk7KIGE6urUXugpI0KQuuK6RWIG',
            user_type: 'public',
            is_enabled: true,
            is_approved: true,
            is_validated: false,
            sections: {wire: true, agenda: true},
            products: [
                {_id: PRODUCTS.wire.sports._id, section: PRODUCTS.wire.sports.product_type},
                {_id: PRODUCTS.agenda.sports._id, section: PRODUCTS.agenda.sports.product_type},
            ],
        },
    },
};
