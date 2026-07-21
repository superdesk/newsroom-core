import React from 'react';
import {mount} from 'enzyme';
import {NotificationPopup} from '../components/NotificationPopup';

import 'tests/setup';

function notification(id: string, item: string, data?: any) {
    return {_id: id, item, resource: 'wire', action: 'topic_matches', _created: '2024-01-01T10:00:00+0000', data};
}

function setup(props: any = {}) {
    return mount(
        <NotificationPopup
            fullUser={{}}
            items={{}}
            count={0}
            notifications={[]}
            loading={false}
            clearNotification={() => undefined}
            clearAll={() => undefined}
            loadNotifications={() => undefined}
            resumeNotifications={() => undefined}
            {...props}
        />
    );
}

describe('NotificationPopup', () => {
    it('only renders notifications whose item can be resolved', () => {
        const wrapper = setup({
            count: 3,
            items: {resolved: {_id: 'resolved', type: 'text', headline: 'Resolved Article'}},
            notifications: [
                notification('n_resolved', 'resolved'),
                notification('n_embedded', 'gone', {item: {_id: 'gone', type: 'text', headline: 'Embedded Article'}}),
                notification('n_orphaned', 'missing'),
            ],
        });

        expect(wrapper.find('.notif__list__item').length).toBe(2);
        expect(wrapper.text()).toContain('Resolved Article');
        expect(wrapper.text()).toContain('Embedded Article');
    });
});
