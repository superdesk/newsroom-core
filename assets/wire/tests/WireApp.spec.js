import React from 'react';
import {mount} from 'enzyme';
import {createStore, applyMiddleware} from 'redux';
import {Provider} from 'react-redux';
import thunk from 'redux-thunk';

import 'tests/setup';

import WireApp from '../components/WireApp';
import {shortHighlightedtext} from '../utils';


function setup(state) {
    const store = createStore(() => state, applyMiddleware(thunk));
    const enzymeWrapper = mount(<Provider store={store}><WireApp /></Provider>);
    return enzymeWrapper;
}

function getActions(enzymeWrapper) {
    return enzymeWrapper.find('WirePreview').props().actions;
}

function getMultiActions(enzymeWrapper) {
    return enzymeWrapper.find('SelectedItemsBar')
        .find('.multi-action-bar__icons').children();
}

function getNames(actions) {
    return actions.map((action) => action.name);
}

describe('WireApp', () => {
    const state = {
        items: [],
        itemsById: {'foo': {}},
        previewItem: 'foo',
        selectedItems: ['foo'],
        context: 'wire',
    };

    it('can filter actions if there is no user or company', () => {
        const enzymeWrapper = setup(state);
        const actions = getActions(enzymeWrapper);
        const names = getNames(actions);
        expect(names).toEqual(['Open', 'Print', 'Copy']);
    });

    it('can show more actions if there is user and company', () => {
        const enzymeWrapper = setup({...state, user: 'foo', company: 'bar'});
        const actions = getActions(enzymeWrapper);
        const names = getNames(actions);
        expect(names).toEqual(['Open', 'Share', 'Print', 'Copy', 'Download', 'Save']);
    });

    it('can pick multi item actions', () => {
        const enzymeWrapper = setup({...state, user: 'foo', company: 'bar'});
        const actions = getMultiActions(enzymeWrapper);
        expect(actions.length).toBe(3);
    });
});


describe('shortHighlightedtext', () => {
    it('returns truncated text with highlighted span', () => {
        const html = `<p>On olemassa myös sellaisia ihmisiä, joiden silmissä 
            jokainen parisuhde muuttuu huonoksi jo muutaman vuoden kuluessa.
            Tällöin kyse voi olla siitä, etteivät he kestä suhteen arkipäiväistymistä,
            kuvailee yksilö- ja pariterapeutti Jouni Pölönen.</p>\n\n
            <p>Pölösen mukaanalkuhuuma <span class="es-highlight">kestää</span> yleensä 1–2 vuotta.
            </p>\n\n<p>–Suhteen alussa on usein paljon seksiä ja ihmiset tuovat parhaat puolensa esiin.
            Kun suhde sitten arkipäiväistyy ja intohimo väistyy arjen tieltä</p>`;
    
        const maxLength = 40;
        const output = shortHighlightedtext(html, maxLength);
        expect(output).toEqual('Pölösen mukaanalkuhuuma <span class="es-highlight">kestää</span> yleensä 1–2 vuotta....');
    });

    it('returns truncated text with highlighted span at the beginning of the line', () => {
        const html = '<p><span class="es-highlight">Turvattomuuden</span> kokemukset sen sijaan voivat\n          altistaa jatkossakin sille, että ihmissuhteet katkeavat herkemmin.\n          Kokemukset turvattomuudesta saattavat heikentää ihmisen kykyä\n          altistaa omaa ja toisen ihmisen mieltä.</p>';
      
        const maxLength = 40;
        const output = shortHighlightedtext(html, maxLength);
        expect(output).toEqual('<span class="es-highlight">Turvattomuuden</span> kokemukset sen sijaan voivat\n          altistaa jatkossakin sille, että ihmissuhteet katkeavat herkemmin.\n          Kokemukset turvattomuudesta saattavat heikentää ihmisen kykyä\n          altistaa omaa ja toisen ihmisen mieltä....');
    });
      
   
      
});
  
