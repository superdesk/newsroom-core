/* eslint-disable no-prototype-builtins */
import {keyBy} from 'lodash';
import moment from 'moment';
import {IAgendaItem} from 'interfaces';
import * as utils from '../utils';


describe('utils', () => {
    describe('groupItems', () => {
        it('returns grouped items per day', () => {
            const items: Array<IAgendaItem> = [
                {
                    _id: 'foo',
                    guid: 'foo',
                    type: 'agenda',
                    item_type: 'event',
                    state: 'scheduled',
                    _created: '2023-11-16T04:00:00+0000',
                    _updated: '2023-11-16T04:00:00+0000',
                    _etag: 'etag123',
                    dates: {start: '2018-10-15T04:00:00+0000', end: '2018-10-15T05:00:00+0000', tz: 'Australia/Sydney'},
                    event: {_id: 'foo'},
                },
                {
                    _id: 'bar',
                    guid: 'bar',
                    type: 'agenda',
                    item_type: 'event',
                    state: 'scheduled',
                    _created: '2023-11-16T04:00:00+0000',
                    _updated: '2023-11-16T04:00:00+0000',
                    _etag: 'etag123',
                    dates: {start: '2018-10-18T06:00:00+0000', end: '2018-10-18T09:00:00+0000', tz: 'Australia/Sydney'},
                    event: {_id: 'bar'},
                },
            ];

            const groupedItems = keyBy(utils.groupItems(items, moment('2018-10-13'), undefined, 'day'), 'date');

            expect(groupedItems.hasOwnProperty('13-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('14-10-2018')).toBe(false);
            expect(groupedItems['15-10-2018']['items']).toEqual(['foo']);
            expect(groupedItems.hasOwnProperty('16-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('17-10-2018')).toBe(false);
            expect(groupedItems['18-10-2018']['items']).toEqual(['bar']);
        });

        it('returns grouped multi day events per day', () => {
            const items: Array<IAgendaItem> = [
                {
                    _id: 'foo',
                    guid: 'foo',
                    type: 'agenda',
                    item_type: 'event',
                    state: 'scheduled',
                    _created: '2023-11-16T04:00:00+0000',
                    _updated: '2023-11-16T04:00:00+0000',
                    _etag: 'etag123',
                    dates: {start: '2018-10-15T04:00:00+0000', end: '2018-10-17T05:00:00+0000', tz: 'Australia/Sydney'},
                    event: {_id: 'foo'}
                },
                {
                    _id: 'bar',
                    guid: 'bar',
                    type: 'agenda',
                    item_type: 'event',
                    state: 'scheduled',
                    _created: '2023-11-16T04:00:00+0000',
                    _updated: '2023-11-16T04:00:00+0000',
                    _etag: 'etag123',
                    dates: {start: '2018-10-17T06:00:00+0000', end: '2018-10-18T09:00:00+0000', tz: 'Australia/Sydney'},
                    event: {_id: 'bar'}
                },
            ];

            const groupedItems = keyBy(utils.groupItems(items, moment('2018-10-15'), undefined, 'day'), 'date');

            expect(groupedItems['15-10-2018']['items']).toEqual(['foo']);
            expect(groupedItems['16-10-2018'].hiddenItems).toEqual(['foo']);
            expect(groupedItems['17-10-2018'].items).toEqual(['bar']);
            expect(groupedItems['17-10-2018'].hiddenItems).toEqual(['foo']);
            expect(groupedItems['18-10-2018'].hiddenItems).toEqual(['bar']);
            expect(groupedItems.hasOwnProperty('19-10-2018')).toBe(false);
        });

        it('returns grouped events with extra days per day', () => {
            const items: Array<IAgendaItem> = [
                {
                    _id: 'foo',
                    guid: 'foo',
                    type: 'agenda',
                    item_type: 'event',
                    state: 'scheduled',
                    _created: '2023-11-16T04:00:00+0000',
                    _updated: '2023-11-16T04:00:00+0000',
                    _etag: 'etag123',
                    dates: {start: '2018-10-15T04:00:00+0000', end: '2018-10-17T05:00:00+0000', tz: 'Australia/Sydney'},
                    display_dates: [{date: '2018-10-13T10:00:00+0000'}],
                    event: {_id: 'foo'}
                }];

            const groupedItems = keyBy(utils.groupItems(items, moment('2018-10-11'), undefined, 'day'), 'date');

            expect(groupedItems.hasOwnProperty('11-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('12-10-2018')).toBe(false);
            expect(groupedItems['13-10-2018'].hiddenItems).toEqual(['foo']);
            expect(groupedItems.hasOwnProperty('14-10-2018')).toBe(false);
            expect(groupedItems['15-10-2018']['items']).toEqual(['foo']);
            expect(groupedItems['16-10-2018'].hiddenItems).toEqual(['foo']);
            expect(groupedItems['17-10-2018'].hiddenItems).toEqual(['foo']);
            expect(groupedItems.hasOwnProperty('18-10-2018')).toBe(false);
        });

        it('returns grouped ad-hoc plan based on extra days', () => {
            const items: Array<IAgendaItem> = [
                {
                    _id: 'foo',
                    guid: 'foo',
                    type: 'agenda',
                    item_type: 'event',
                    state: 'scheduled',
                    _created: '2023-11-16T04:00:00+0000',
                    _updated: '2023-11-16T04:00:00+0000',
                    _etag: 'etag123',
                    dates: {start: '2018-10-17T04:00:00+0000', end: '2018-10-17T04:00:00+0000'},
                    display_dates: [
                        {date: '2018-10-16T04:00:00+0000'},
                        {date: '2018-10-18T04:00:00+0000'}
                    ],
                }];

            const groupedItems = keyBy(utils.groupItems(items, moment('2018-10-15'), undefined, 'day'), 'date');

            expect(groupedItems.hasOwnProperty('15-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('17-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('16-10-2018')).toBe(true);
            expect(groupedItems.hasOwnProperty('18-10-2018')).toBe(true);
            expect(groupedItems['16-10-2018'].items).toEqual([]);
            expect(groupedItems['16-10-2018'].hiddenItems).toEqual(['foo']);
            expect(groupedItems['18-10-2018'].items).toEqual([]);
            expect(groupedItems['18-10-2018'].hiddenItems).toEqual(['foo']);
        });

        it('returns grouped ad-hoc plan with no extra days', () => {
            const items: Array<IAgendaItem> = [
                {
                    _id: 'foo',
                    guid: 'foo',
                    type: 'agenda',
                    item_type: 'event',
                    state: 'scheduled',
                    _created: '2023-11-16T04:00:00+0000',
                    _updated: '2023-11-16T04:00:00+0000',
                    _etag: 'etag123',
                    dates: {start: '2018-10-17T04:00:00+0000', end: '2018-10-17T04:00:00+0000'},
                    display_dates: [{date: '2018-10-17T04:00:00+0000'}],
                }];

            const groupedItems = keyBy(utils.groupItems(items, moment('2018-10-15'), undefined, 'day'), 'date');

            expect(groupedItems.hasOwnProperty('15-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('16-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('17-10-2018')).toBe(true);
            expect(groupedItems.hasOwnProperty('18-10-2018')).toBe(false);
            expect(groupedItems['17-10-2018']['items']).toEqual(['foo']);
        });
    });

    describe('listItems', () => {
        it('of event with planning items', () => {
            const items: Array<IAgendaItem> = [
                {
                    _id: 'foo',
                    guid: 'foo',
                    type: 'agenda',
                    item_type: 'event',
                    state: 'scheduled',
                    _created: '2023-11-16T04:00:00+0000',
                    _updated: '2023-11-16T04:00:00+0000',
                    _etag: 'etag123',
                    dates: {start: '2018-10-15T04:00:00+0000', end: '2018-10-15T05:00:00+0000', tz: 'Australia/Sydney'},
                    display_dates: [
                        {date: '2018-10-14T04:00:00+0000'},
                        {date: '2018-10-16T04:00:00+0000'},
                    ],
                    event: {_id: 'foo'},
                    coverages: [
                        {
                            'scheduled': '2018-10-15T04:00:00+0000',
                            'planning_id': 'plan1',
                            'coverage_id': 'coverage1',
                            coverage_type: 'text',
                            coverage_status: 'coverage intended',
                            workflow_status: 'assigned',
                        },
                        {
                            'scheduled': '2018-10-14T04:00:00+0000',
                            'planning_id': 'plan1',
                            'coverage_id': 'coverage2',
                            coverage_type: 'text',
                            coverage_status: 'coverage intended',
                            workflow_status: 'assigned',
                        },
                        {
                            'scheduled': '2018-10-16T04:00:00+0000',
                            'planning_id': 'plan2',
                            'coverage_id': 'coverage3',
                            coverage_type: 'text',
                            coverage_status: 'coverage intended',
                            workflow_status: 'assigned',
                        }
                    ],
                    planning_items: [
                        {
                            '_id': 'plan1',
                            'guid': 'plan1',
                            type: 'agenda',
                            item_type: 'planning',
                            state: 'scheduled',
                            _created: '2023-11-16T04:00:00+0000',
                            _updated: '2023-11-16T04:00:00+0000',
                            _etag: 'etag123',
                            'planning_date': '2018-10-15T04:30:00+0000',
                            dates: {start: '2018-10-15T04:30:00+0000', end: '2018-10-15T04:30:00+0000'},
                            'coverages': [
                                {
                                    'scheduled': '2018-10-15T04:00:00+0000',
                                    'planning_id': 'plan1',
                                    'coverage_id': 'coverage1',
                                    coverage_type: 'text',
                                    coverage_status: 'coverage intended',
                                    workflow_status: 'assigned',
                                },
                                {
                                    'scheduled': '2018-10-14T04:00:00+0000',
                                    'planning_id': 'plan1',
                                    'coverage_id': 'coverage2',
                                    coverage_type: 'text',
                                    coverage_status: 'coverage intended',
                                    workflow_status: 'assigned',
                                }
                            ],
                        },
                        {
                            '_id': 'plan2',
                            'guid': 'plan2',
                            type: 'agenda',
                            item_type: 'planning',
                            state: 'scheduled',
                            _created: '2023-11-16T04:00:00+0000',
                            _updated: '2023-11-16T04:00:00+0000',
                            _etag: 'etag123',
                            'planning_date': '2018-10-15T04:30:00+0000',
                            dates: {start: '2018-10-15T04:30:00+0000', end: '2018-10-15T04:30:00+0000'},
                            'coverages': [{
                                'scheduled': '2018-10-16T04:00:00+0000',
                                'planning_id': 'plan2',
                                'coverage_id': 'coverage3',
                                coverage_type: 'text',
                                coverage_status: 'coverage intended',
                                workflow_status: 'assigned',
                            }],
                        }
                    ]
                }
            ];

            const groupedItems = utils.groupItems(items, moment('2018-10-11'), undefined, 'day');
            const itemsById = keyBy(items, '_id');
            const hiddenGroupsShown = {
                '14-10-2018': true,
                '15-10-2018': true,
                '16-10-2018': true,
            };
            const listItems = keyBy(utils.getListItems(groupedItems, itemsById, hiddenGroupsShown), 'group');

            expect(groupedItems.hasOwnProperty('11-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('12-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('13-10-2018')).toBe(false);
            expect(listItems.hasOwnProperty('14-10-2018')).toBe(true);
            expect(listItems.hasOwnProperty('15-10-2018')).toBe(true);
            expect(listItems.hasOwnProperty('16-10-2018')).toBe(true);
            expect(listItems['14-10-2018']['_id']).toBe('foo');
            expect(listItems['14-10-2018']?.plan).toBe('plan1');
            expect(listItems['15-10-2018']._id).toBe('foo');
            expect(listItems['15-10-2018'].plan).toBe('plan1');
            expect(listItems['16-10-2018']['_id']).toBe('foo');
            expect(listItems['16-10-2018']?.plan).toBe('plan2');
        });

        it('planning items without coverages associated with event are also displayed', () => {
            const items: Array<IAgendaItem> = [
                {
                    _id: 'foo',
                    guid: 'foo',
                    type: 'agenda',
                    item_type: 'event',
                    state: 'scheduled',
                    _created: '2023-11-16T04:00:00+0000',
                    _updated: '2023-11-16T04:00:00+0000',
                    _etag: 'etag123',
                    dates: {start: '2018-10-15T04:00:00+0000', end: '2018-10-15T05:00:00+0000', tz: 'Australia/Sydney'},
                    display_dates: [{date: '2018-10-14T04:00:00+0000'}],
                    event: {_id: 'foo'},
                    coverages: [],
                    planning_items: [
                        {
                            '_id': 'plan1',
                            'guid': 'plan1',
                            'planning_date': '2018-10-14T04:30:00+0000',
                            dates: {start: '2018-10-14T04:30:00+0000', end: '2018-10-14T04:30:00+0000'},
                            type: 'agenda',
                            item_type: 'planning',
                            state: 'scheduled',
                            _created: '2023-11-16T04:00:00+0000',
                            _updated: '2023-11-16T04:00:00+0000',
                            _etag: 'etag123',
                        }
                    ]
                }
            ];

            const groupedItems = utils.groupItems(items, moment('2018-10-11'), undefined, 'day');
            const itemsById = keyBy(items, '_id');
            const hiddenGroupsShown = {
                '14-10-2018': true,
                '15-10-2018': true,
            };
            const listItems = keyBy(utils.getListItems(groupedItems, itemsById, hiddenGroupsShown), 'group');

            expect(groupedItems.hasOwnProperty('11-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('12-10-2018')).toBe(false);
            expect(groupedItems.hasOwnProperty('13-10-2018')).toBe(false);
            expect(listItems.hasOwnProperty('14-10-2018')).toBe(true);
            expect(listItems.hasOwnProperty('15-10-2018')).toBe(true);
            expect(listItems['14-10-2018']['_id']).toBe('foo');
            expect(listItems['14-10-2018']?.plan).toBe('plan1');
            expect(listItems['15-10-2018']['_id']).toBe('foo');
            expect(listItems['15-10-2018']?.plan).toBe(undefined);
        });
    });

    it('groupItems restricting groups to min and max dates', () => {
        const items: Array<IAgendaItem> = [{
            _id: 'event1',
            guid: 'event1',
            type: 'agenda',
            item_type: 'event',
            state: 'scheduled',
            _created: '2023-11-16T04:00:00+0000',
            _updated: '2023-11-16T04:00:00+0000',
            _etag: 'etag123',
            dates: {start: '2018-10-15T04:00:00+0000', end: '2018-10-15T05:00:00+0000', tz: 'Australia/Sydney'},
            event: {_id: 'event1'},
        }, {
            _id: 'event2',
            guid: 'event2',
            type: 'agenda',
            item_type: 'event',
            state: 'scheduled',
            _created: '2023-11-16T04:00:00+0000',
            _updated: '2023-11-16T04:00:00+0000',
            _etag: 'etag123',
            dates: {start: '2018-10-16T04:00:00+0000', end: '2018-10-16T05:00:00+0000', tz: 'Australia/Sydney'},
            event: {_id: 'event2'},
        }, {
            _id: 'event3',
            guid: 'event3',
            type: 'agenda',
            item_type: 'event',
            state: 'scheduled',
            _created: '2023-11-16T04:00:00+0000',
            _updated: '2023-11-16T04:00:00+0000',
            _etag: 'etag123',
            dates: {start: '2018-10-17T04:00:00+0000', end: '2018-10-17T05:00:00+0000', tz: 'Australia/Sydney'},
            event: {_id: 'event3'},
        }];

        const getGroupedItems = (minDate: moment.Moment, maxDate?: moment.Moment) => keyBy(
            utils.groupItems(items, minDate, maxDate, 'day', false),
            'date'
        );
        let groupedItems = getGroupedItems(moment('2018-10-14'), moment('2018-10-18'));

        expect(groupedItems['15-10-2018'].items).toEqual(['event1']);
        expect(groupedItems['16-10-2018'].items).toEqual(['event2']);
        expect(groupedItems['17-10-2018'].items).toEqual(['event3']);

        groupedItems = getGroupedItems(moment('2018-10-14'), moment('2018-10-15'));
        expect(groupedItems['15-10-2018'].items).toEqual(['event1']);
        expect(groupedItems['16-10-2018']).toBeUndefined();
        expect(groupedItems['17-10-2018']).toBeUndefined();

        groupedItems = getGroupedItems(moment('2018-10-16'), moment('2018-10-18'));
        expect(groupedItems['15-10-2018']).toBeUndefined();
        expect(groupedItems['16-10-2018'].items).toEqual(['event2']);
        expect(groupedItems['17-10-2018'].items).toEqual(['event3']);

        groupedItems = getGroupedItems(moment('2018-10-16'));
        expect(groupedItems['15-10-2018']).toBeUndefined();
        expect(groupedItems['16-10-2018'].items).toEqual(['event2']);
        expect(groupedItems['17-10-2018'].items).toEqual(['event3']);
    });
});
