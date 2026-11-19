import React from 'react';
import {mount, ReactWrapper} from 'enzyme';
import {Provider} from 'react-redux';
import {createStore} from 'redux';
import moment from 'moment-timezone';

import {IUser} from 'interfaces';
import {getScheduledNotificationConfig} from 'utils';
import {TimePicker} from 'components/cards/TimePicker';
import {EditNotificationScheduleModal} from 'user-profile/components/EditNotificationScheduleModal';

import 'tests/setup';

describe('EditNotificationScheduleModal', () => {
    let wrapper: ReactWrapper;

    const setup = (times: Array<string>) => {
        const Component = EditNotificationScheduleModal.WrappedComponent;
        const updateSchedule = jasmine.createSpy('updateUserNotificationSchedule');
        const user: IUser = {
            _id: 'user',
            first_name: '',
            last_name: '',
            email: '',
            phone: '',
            mobile: '',
            role: '',
            country: '',
            company: '',
            user_type: 'public',
            locale: 'en',
            sections: {},
            notification_schedule: {
                timezone: moment.tz.guess(),
                times,
                pause_from: '2024-08-23',
                pause_to: '2024-08-25',
            },
        };

        wrapper = mount(
            <Provider store={createStore(() => ({modal: {formValid: true}}))}>
                <Component
                    data={{user}}
                    modalFormInvalid={() => undefined}
                    modalFormValid={() => undefined}
                    updateUserNotificationSchedule={updateSchedule}
                />
            </Provider>
        );

        return updateSchedule;
    };

    afterEach(() => {
        wrapper.unmount();
    });

    it('adds and saves a configured default time when the schedule is empty', () => {
        const updateSchedule = setup([]);
        const defaultTime = getScheduledNotificationConfig().default_times[0];

        expect(wrapper.find(TimePicker).length).toBe(0);
        wrapper.find('button[data-test-id="add-schedule"]').simulate('click');

        expect(wrapper.find(TimePicker).prop('value')).toBe(defaultTime);
        wrapper.find('form').simulate('submit');
        expect(updateSchedule).toHaveBeenCalledWith({
            timezone: moment.tz.guess(),
            times: [defaultTime],
        });
    });

    it('copies the last time when adding to an existing schedule', () => {
        setup(['09:15']);

        wrapper.find('button[data-test-id="add-schedule"]').simulate('click');

        expect(wrapper.find(TimePicker).map((picker) => picker.prop('value'))).toEqual(['09:15', '09:15']);
    });

    it('adds midnight when neither the schedule nor the configured defaults contain times', () => {
        const config = getScheduledNotificationConfig();
        const defaultTimes = config.default_times;

        config.default_times = [];
        try {
            setup([]);
            wrapper.find('button[data-test-id="add-schedule"]').simulate('click');

            expect(wrapper.find(TimePicker).prop('value')).toBe('00:00');
        } finally {
            config.default_times = defaultTimes;
        }
    });
});
