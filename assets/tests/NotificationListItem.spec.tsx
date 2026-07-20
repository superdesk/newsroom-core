import React from 'react';
import {mount} from 'enzyme';
import NotificationListItem from '../components/NotificationListItem';

import 'tests/setup';

const notification = {
    _id: 'user_id_item_id',
    item: 'item_id',
    resource: 'wire',
    action: 'topic_matches',
    _created: '2024-01-01T10:00:00+0000',
};

function setup(item: any) {
    return mount(
        <NotificationListItem
            notification={notification}
            item={item}
            clearNotification={() => undefined}
        />
    );
}

describe('NotificationListItem', () => {
    it('renders the notification when the item is there', () => {
        const wrapper = setup({_id: 'item_id', type: 'text', headline: 'Demo Article'});

        expect(wrapper.find('.notif__list__item').length).toBe(1);
        expect(wrapper.text()).toContain('Demo Article');
    });

    it('renders nothing when the item is missing', () => {
        expect(setup(undefined).isEmptyRender()).toBe(true);
        expect(setup(null).isEmptyRender()).toBe(true);
    });

    it('clears the notification by its item id', () => {
        const clearNotification = jasmine.createSpy('clearNotification');
        const wrapper = mount(
            <NotificationListItem
                notification={notification}
                item={{_id: 'item_id', type: 'text', headline: 'Demo Article'}}
                clearNotification={clearNotification}
            />
        );

        wrapper.find('button').first().simulate('click');

        expect(clearNotification).toHaveBeenCalledWith('item_id');
    });
});
