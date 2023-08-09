import {get} from 'lodash';
import {createSelector} from 'reselect';

export const monitoringProfileToEdit = (state: any) => get(state, 'monitoringProfileToEdit') || null;
export const company = (state: any) => get(state, 'company') || null;
export const scheduleMode = (state: any) => get(state, 'scheduleMode') || false;
export const monitoringListById = (state: any) => get(state, 'monitoringListById') || null;
export const monitoringProfileList = (state: any) => get(state, 'monitoringList') || null;

export const monitoringList = createSelector([monitoringListById, monitoringProfileList, scheduleMode],
    (pById: any, ps: any, sched: any) => {
        const allProfiles = ps.map((id: any) => pById[id]);
        if (!sched) {
            return allProfiles;
        }

        return allProfiles.filter((p: any) => get(p, 'schedule.interval'));
    });
