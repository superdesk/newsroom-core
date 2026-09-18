import React from 'react';
import moment from 'moment';
import {mount} from 'enzyme';

import {formatDate} from 'utils';
import {AgendaListGroupHeader} from '../components/AgendaListGroupHeader';

import 'tests/setup';

function setup(props: any) {
    return mount(
        <AgendaListGroupHeader
            group={props.group}
            itemIds={props.itemIds}
            itemsById={props.itemsById}
            itemsShown={props.itemsShown}
            toggleHideItems={props.toggleHideItems ?? (() => undefined)}
        />
    );
}

describe('AgendaListGroupHeader', () => {
    const group = '01-08-2026';
    const itemsById = {a: {_id: 'a'}, b: {_id: 'b'}};
    const itemIds = ['a', 'b'];

    describe('when the group is collapsed (itemsShown=false)', () => {
        it('renders the hidden indicator and a "Show all" button', () => {
            const wrapper = setup({group, itemIds, itemsById, itemsShown: false});

            expect(wrapper.find('span.badge').text()).toBe('2');
            expect(wrapper.find('.list-group-header__title').text()).toBe('More hidden');
            expect(wrapper.find('.list-group-header__actions button').text()).toBe('Show all');
        });
    });

    describe('when the group is expanded (itemsShown=true)', () => {
        it('hides the indicator, leaving only the "Hide" button', () => {
            const wrapper = setup({group, itemIds, itemsById, itemsShown: true});

            // STT-1726: the "N More hidden" indicator must be gone once shown
            expect(wrapper.find('span.badge').length).toBe(0);
            expect(wrapper.find('.list-group-header__title').length).toBe(0);
            expect(wrapper.find('.list-group-header__actions button').text()).toBe('Hide');
        });
    });

    describe('with coverages scheduled on the group date', () => {
        const scheduled = '2026-08-05T12:00:00';
        const covGroup = formatDate(moment(scheduled));
        const covItemsById = {
            e: {_id: 'e', coverages: [{coverage_id: 'c1', coverage_type: 'text', scheduled}]},
        };

        it('renders coverage icons while collapsed', () => {
            const wrapper = setup({group: covGroup, itemIds: ['e'], itemsById: covItemsById, itemsShown: false});

            expect(wrapper.find('.list-group-header__coverage-item').length).toBe(1);
        });

        it('hides coverage icons once expanded', () => {
            const wrapper = setup({group: covGroup, itemIds: ['e'], itemsById: covItemsById, itemsShown: true});

            expect(wrapper.find('.list-group-header__coverage-item').length).toBe(0);
        });
    });
});
