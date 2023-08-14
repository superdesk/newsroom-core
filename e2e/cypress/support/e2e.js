import {NAVIGATIONS} from '../fixtures/navigations';
import {PRODUCTS} from '../fixtures/products';
import {COMPANIES} from '../fixtures/companies';
import {USERS} from '../fixtures/users';
import {WIRE_ITEMS} from '../fixtures/wire';

export const baseUrl = 'http://localhost:5050/';

export function constructUrl(base, uri) {
    return base.replace(/\/$/, '') + uri;
}

function getBackendUrl(uri) {
    return constructUrl(baseUrl, uri);
}

function backendRequest(params) {
    if (params.uri) {
        params.url = getBackendUrl(params.uri);
        delete params.uri;
    }

    if (params.json) {
        params.body = params.json;
        delete params.json;
    }

    params.timeout = params.timeout || 10000;

    return cy.request(params);
}

function resetApp() {
    backendRequest({
        uri: '/api/e2e/init',
        method: 'POST',
        timeout: 40000,
        json: {},
        retryOnStatusCodeFailure: false,
    });
}

export function setup(url='') {
    cy.log('Common.App.setup');
    resetApp();
    cy.visit(baseUrl + url);
}

export function addResources(resources) {
    cy.log('Common.App.addResources');
    backendRequest({
        uri: '/api/e2e/populate_resources',
        method: 'POST',
        timeout: 40000,
        json: {resources: resources},
    });
}

export function addDefaultResources() {
    addResources([{
        resource: 'navigations', items: [
            NAVIGATIONS.wire.all,
            NAVIGATIONS.wire.sports,
            NAVIGATIONS.agenda.sports,
        ],
    }, {
        resource: 'products', items: [
            PRODUCTS.wire.all,
            PRODUCTS.wire.sports,
            PRODUCTS.agenda.sports,
        ],
    }, {
        resource: 'companies', items: [
            COMPANIES.sofab,
            COMPANIES.foobar,
        ],
    }, {
        resource: 'users', items: [
            USERS.foobar.admin,
            USERS.foobar.monkey,
        ],
    }]);
}

export function addDefaultWireItems() {
    addResources([{
        resource: 'items', use_resource_service: false, items: [
            WIRE_ITEMS.syd_weather_1,
        ],
    }]);
}

export function addAllWireItems() {
    addResources([{
        resource: 'items', use_resource_service: false, items: [
            WIRE_ITEMS.syd_weather_1,
            WIRE_ITEMS.bris_traffic_1,
        ],
    }]);
}
