import {IUser} from 'interfaces';
import server from 'server';
import {notify} from 'utils';

export function postNotificationSchedule(userId: string, schedule: Omit<IUser['notification_schedule'], 'last_run_time'>, message: string):Promise<void> {    
    return server.post(`/users/${userId}/notification_schedules`, schedule)
        .then(() => {
            notify.success(message);
        });
}
